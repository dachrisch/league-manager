//import teams from "../data/teams.json";
import { Button } from "react-bootstrap";
import TeamCard from "./TeamCard";
import { useState } from "react";

let teamDataJSON = require("../data/teams.json");
const teamsWithKeys = teamDataJSON.teamlist.map((obj: any, index: any) => ({
  ...obj,
  key: index,
}));
console.log(teamDataJSON.teamlist);

function TeamOverview(this: any) {
  return (
    <>
      <Button>zur Scorecard</Button>
      {teamsWithKeys.map((team: any) => (
        <div>
          <TeamCard index={team.key} teams={teamsWithKeys} />
        </div>
      ))}
    </>
  );
}

export default TeamOverview;
