import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import { ListResult } from "../Components/ListResult";
import { PageNavigation } from "../Components/PageNavigation";
import { makeStyles } from "@material-ui/core/styles";
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import TopBar from "../Components/TopBar";
import axios from "axios";
import Grid from "@material-ui/core/Grid";
import Box from "@material-ui/core/Box";
import Divider from "@material-ui/core/Divider";

const useStyles = makeStyles(theme => ({
  root: {
    marginLeft: ({ matches }) =>
      matches ? theme.spacing(1.5) : theme.spacing(15)
  },
  stats: {
    color: "#52565a",
    fontSize: 14,
    fontFamily: "Arial",
    marginTop: theme.spacing(2),
    marginLeft: theme.spacing(1),
    marginBottom: theme.spacing(2)
  }
}));

export const SearchingPage = () => {
  const [results, setResults] = useState([]);
  const [querySpeed, setQuerySpeed] = useState("");
  const [numberResultsFound, setNumberResultsFound] = useState(0);
  const [searchText, setSearchText] = useState([]);
  const [searchLemmatized, setSearchLemmatized] = useState([]);
  const history = useHistory();
  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.down(680));
  const classes = useStyles({ matches });

  const getParams = () => {
    const decoded = decodeURI(history.location.search)
      .split(/^(\?q=)?/)[2]
      .split("&");
    const params = {
      query: decoded[0],
      start: decoded[1].replace("start=", "")
    };
    return params;
  };

  const getData = async () => {
    const { query, start } = getParams();
    const reply = await axios({
      method: "get",
      url: "http://127.0.0.1:5000/api",
      params: {
        query: query,
        start: start
      }
    });
    setResults(reply.data.results);
    setSearchText(query);
    setQuerySpeed(reply.data.query_speed);
    setNumberResultsFound(reply.data.number_results_found);
    setSearchLemmatized(reply.data.search_lemmatized);
  };

  const onSearch = () => {
    if (searchText.length > 3) {
      history.push(`/search?q=${searchText}&start=0`);
      window.scrollTo(0, 0);
    }
  };

  useEffect(() => {
    getData();
    // eslint-disable-next-line
  }, [history.location.search]);

  return (
    <>
      <TopBar
        searchText={searchText}
        setSearchText={setSearchText}
        onSearch={onSearch}
      />
      <Divider />
      <div className={classes.root}>
        <Box className={classes.stats}>
          About {(Math.floor(numberResultsFound / 100) * 100).toLocaleString()}{" "}
          results ({querySpeed} seconds)
        </Box>
        <Grid container direction="column">
          {results.map(result => (
            <Grid item key={result.url}>
              <ListResult
                url={result.url}
                title={result.title}
                snippet={result.snippet}
                searchLemmatized={searchLemmatized}
              />
            </Grid>
          ))}
        </Grid>
        <PageNavigation
          searchText={searchText}
          numberResultsFound={numberResultsFound}
        />
      </div>
    </>
  );
};
