import {useEffect, useState} from 'react';
import {getPasscheckData} from '../common/games';
import {Game, GameList, GameOverviewInfo, Gameday} from '../common/types';
import useMessage from '../hooks/useMessage';
import {ApiError} from '../utils/api';
import GameCard from './GameCard';
import {Form} from 'react-bootstrap';
import {useNavigate, useParams} from 'react-router-dom';

function GameOverview() {
  const [games, setGames] = useState<GameList>([]);
  const [gamedays, setGamedays] = useState<Gameday[]>([]);
  const [officials, setOfficials] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [showAllGamedays, setShowAllGamedays] = useState<boolean>(false);
  const {setMessage} = useMessage();
  const {gamedayId} = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    console.log('gamedayId GameOverview', gamedayId);
    getPasscheckData(gamedayId)
      .then((result: GameOverviewInfo) => {
        setGames(result.games);
        setOfficials(result.officialsTeamName);
        setGamedays(result.gamedays);
        setMessage({text: ''});
        setLoading(false);
      })
      .catch((error: ApiError) => {
        setMessage({text: error.message});
      });
  }, [gamedayId]);

  return (
    <>
      {loading && <p>loading...</p>}
      {!loading && (
        <>
          <h1>Herzlich willkommen, {officials}.</h1>
          <div>Bitte ein Spiel auswählen:</div>
          {games.map((game: Game, index: number) => (
            <GameCard key={index} game={game} />
          ))}
          <div className='row mt-5'>
            <div className='col'>
              <Form.Check
                type={'checkbox'}
                id='select-all-gamedays-checkbox'
                label='Alle Spiele auswählen'
                onClick={() => setShowAllGamedays(!showAllGamedays)}
              />
            </div>
          </div>
          {showAllGamedays && (
            <div className='row mt-2'>
              <div className='col'>
                <Form.Select
                  onChange={(event) =>
                    navigate(`/gameday/${event.target.value}`)
                  }
                >
                  <option>Bitte Spieltag auswählen</option>
                  {gamedays.map((currentGameday, index) => (
                    <option key={index} value={currentGameday.id}>
                      {currentGameday.name}
                    </option>
                  ))}
                </Form.Select>
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
}

export default GameOverview;
