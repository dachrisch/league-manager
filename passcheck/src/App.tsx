import Headerdata from "./components/Headerdata";
import PlayersOverview from "./components/PlayersOverview";
import TeamOverview from "./components/TeamOverview";

function App() {
  return (
    <>
      <Headerdata />
      <div>
        {/* <TeamOverview /> */}
        <PlayersOverview />
      </div>
    </>
  );
}

export default App;
