import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Pagination from "@material-ui/lab/Pagination";
import { Box } from "@material-ui/core/";
import { useHistory } from "react-router-dom";

const useStyles = makeStyles(theme => ({
  root: {
    "& > *": {
      marginBottom: theme.spacing(5),
      margin: theme.spacing(1.5),
      textAlign: "center"
    }
  }
}));

export const PageNavigation = ({ searchText, numberResultsFound }) => {
  const history = useHistory();
  const [page, setPage] = useState(0);

  const classes = useStyles();
  const numberPages = Math.floor(numberResultsFound / 20);
  const calculateCurrentPage = currentNumber => {
    return Math.floor(currentNumber / 20);
  };
  const defaultPageDecoder = () => {
    const decoded = decodeURI(history.location.search)
      .split(/^(\?q=)?/)[2]
      .split("&");
    return Number(decoded[1].replace("start=", ""));
  };

  const handleChange = (event, value) => {
    history.push(`/search?q=${searchText}&start=${(value - 1) * 20}`);
    window.scrollTo(0, 0);
  };

  useEffect(() => {
    setPage(defaultPageDecoder());
    // eslint-disable-next-line
  }, [history.location.search]);

  return (
    <Box mr="auto" width="100%" maxWidth={740}>
      <div className={classes.root}>
        <Pagination
          size="large"
          count={numberPages}
          boundaryCount={1}
          siblingCount={3}
          page={calculateCurrentPage(page + 20)}
          onChange={handleChange}
        />
      </div>
    </Box>
  );
};
