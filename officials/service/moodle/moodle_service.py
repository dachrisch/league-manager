import concurrent
from concurrent.futures import ThreadPoolExecutor
from time import time
from datetime import datetime

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import QuerySet

from gamedays.models import Association, Team
from officials.models import OfficialLicenseHistory, Official
from officials.service.boff_license_calculation import LicenseCalculator
from officials.service.moodle.moodle_api import MoodleApi, ApiUserInfo, ApiCourses, ApiParticipants, ApiUpdateUser, \
    ApiCourse, ApiParticipant


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        execution_time = end_time - start_time
        minutes = int(execution_time // 60)
        seconds = int(execution_time % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        return result, formatted_time

    return wrapper


class MoodleService:
    def __init__(self):
        self.moodle_api = MoodleApi()
        self.license_history: QuerySet[OfficialLicenseHistory] = OfficialLicenseHistory.objects.none()
        self.license_calculator = LicenseCalculator()

    def get_all_users_for_course(self, course_id) -> []:
        participants: ApiParticipants = self.moodle_api.get_participants_for_course(course_id)
        participants_ids = []
        for current_participant in participants.get_all():
            participants_ids += [current_participant.user_id]
        return participants_ids

    def get_course_by_id(self, course_id) -> ApiCourse:
        return self.moodle_api.get_courses(course_id).get_all()[0]

    @measure_execution_time
    def update_licenses(self, course_ids: str = None):
        courses: ApiCourses = self.moodle_api.get_courses(course_ids)
        missing_team_names = set()
        result_list = []
        missed_officials_list = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit each course update task to the thread pool
            futures = {executor.submit(self.get_participants_from_course, current_course): current_course for
                       current_course in
                       courses.get_all()}

            for future in concurrent.futures.as_completed(futures):
                course = futures[future]
                try:
                    team_name_set, missed_official, course_result = future.result()
                    missing_team_names.update(team_name_set)
                    missed_officials_list += missed_official
                    result_list += [course_result]
                except Exception as e:
                    print(f"An error occurred while processing course {course}: {e}")

        return {
            'items_result_list': len(result_list),
            'items_missed_officials': len(missed_officials_list),
            'result_list': result_list,
            'missed_officials': missed_officials_list,
            'missing_team_names': sorted(missing_team_names),
        }

    def get_participants_from_course(self, course: ApiCourse):
        result = self.get_participants_from_course_with_time_measure(course)
        team_name_set, missed_official, officials = result[0]
        formatted_time = result[1]
        course_result = {
            "course": course.get_name(),
            "execution_time": formatted_time,
            "officials_count": len(officials),
            "officials": officials,
        }
        return team_name_set, missed_official, course_result

    @measure_execution_time
    def get_participants_from_course_with_time_measure(self, course: ApiCourse):
        if course.is_relevant():
            year = datetime.today().year
            self.license_history = OfficialLicenseHistory.objects.filter(created_at__year=year)
            return self.get_participants_from_relevant_course(course)
        return set(), [], []

    def get_participants_from_relevant_course(self, course):
        participants: ApiParticipants = self.moodle_api.get_participants_for_course(course.get_id())
        result_list = []
        missed_officials_list = []
        missing_teams_list = set()
        for current_participant in participants.get_all():
            team_name, missed_official, official = self.get_info_of_user(course, current_participant)
            if team_name is not None:
                missing_teams_list.add(team_name)
            missed_officials_list += missed_official
            result_list += official

        return missing_teams_list, missed_officials_list, result_list

    def get_info_of_user(self, course, participant: ApiParticipant):
        if participant.has_result():
            return self.get_info_of_user_with_result(course, participant)
        return None, [], []

    def get_info_of_user_with_result(self, course, participant):
        user_info: ApiUserInfo = self.moodle_api.get_user_info_by_id(participant.get_user_id())
        team_description = user_info.get_team()
        team_id = user_info.get_team_id()
        team: Team = self._get_first(Team.objects.filter(pk=team_id))
        if team is None:
            missed_officials = [
                f'{course.get_id()}: {user_info.id} - {user_info.get_last_name()} '
                f'-> fehlendes Team: {team_description}']
            return team_description, missed_officials, []
        else:
            official = self.create_new_or_update_existing_official(user_info)
        self.create_new_or_update_license_history(official, course, participant)
        return None, [], [str(official)]

    def create_new_or_update_license_history(self, official, course, participant: ApiParticipant):
        license_history_to_update: OfficialLicenseHistory = self._get_first(self.license_history.filter(
            official=official,
            created_at__year=course.get_year()
        ))
        if license_history_to_update is not None:
            license_history_to_update.license_id = self.license_calculator.calculate(
                course.get_license_id(),
                participant.get_result()
            )
            license_history_to_update.result = participant.get_result()
        else:
            license_history_to_update = self.create_new_license_history(course, official, participant)
        license_history_to_update.save()
        api_user = ApiUpdateUser(official.external_id, official.pk, license_history_to_update.license_id)
        self.moodle_api.update_user(api_user)

    def create_new_or_update_existing_official(self, user_info) -> Official:
        official = self._get_first(Official.objects.filter(external_id=user_info.get_id()))
        if official is None:
            official = Official()
            official.external_id = user_info.get_id()
        official.first_name = user_info.get_first_name()
        official.last_name = user_info.get_last_name()
        official.team = self._get_first(Team.objects.filter(pk=user_info.get_team_id()))
        if user_info.whistle_for_association():
            official.association = Association.objects.get(name=user_info.get_association())
        official.save()
        return official

    def create_new_license_history(self, course, official, participant) -> OfficialLicenseHistory:
        license_id = self.license_calculator.calculate(course.get_license_id(), participant.get_result())
        return OfficialLicenseHistory(
            created_at=course.get_date(),
            license_id=license_id,
            official=official,
            result=participant.get_result()
        )

    # noinspection PyMethodMayBeStatic
    def _get_first(self, query_set: QuerySet):
        if query_set.count() > 1:
            raise MultipleObjectsReturned(f'For the following QuerySet multiple items found {query_set} '
                                          f'with WHERE-clause {query_set.query.where}')
        return query_set.first()

    def get_user_info_by(self, external_id) -> ApiUserInfo:
        return self.moodle_api.get_user_info_by_id(external_id)

    def login(self, username, password) -> int:
        self.moodle_api.confirm_user_auth(username, password)
        user = self.moodle_api.get_user_info_by_username(username)
        if user == -1:
            user = self.moodle_api.get_user_info_by_email(username)
        return Official.objects.get(external_id=user.get_id()).pk
