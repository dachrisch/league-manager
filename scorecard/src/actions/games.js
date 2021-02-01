import axios from "axios";
import { returnErrors } from "./messages";
import { GET_GAMES, SET_SELECTED_GAME } from "./types";

import { tokenConfig } from "../actions/auth";

export const getGames = (gamedayId) => async (dispatch, getState) => {
  await axios
    .get(`/api/gameday/${gamedayId}/details?get=schedule&orient=records`)
    .then((res) => {
      dispatch({
        type: GET_GAMES,
        payload: res.data,
      });
    })
    .catch((err) =>
      dispatch(returnErrors(err.response.data, err.response.status))
    );
};

export const setSelectedGame = (selectedGame) => (dispatch) => {
  dispatch({
    type: SET_SELECTED_GAME,
    payload: selectedGame,
  });
};
