import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import logo from "../assets/gugol-300.png";
import SearchBar from "../Components/SearchBar";
import { makeStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";

const useStyles = makeStyles(theme => ({
  root: {
    height: "100vh"
  },
  container: {
    position: "absolute",
    top: "15%"
  },
  marginContainer: {
    marginTop: theme.spacing(3)
  },
  button: {
    textTransform: "none"
  }
}));

export const LandingPage = () => {
  const classes = useStyles();
  const [searchText, setSearchText] = useState("");
  const history = useHistory();

  const onSearch = () => {
    history.push(`/search?q=${searchText}&start=0`);
    window.scrollTo(0, 0);
  };

  return (
    <div className={classes.root}>
      <Grid container direction="column" className={classes.container}>
        <Grid container justify="center" item>
          <img src={logo} alt="Gugol" />
        </Grid>
        <Grid
          container
          justify="center"
          item
          className={classes.marginContainer}
        >
          <SearchBar
            searchText={searchText}
            setSearchText={setSearchText}
            onSearch={onSearch}
          />
        </Grid>
        <Grid
          container
          justify="center"
          item
          className={classes.marginContainer}
        >
          <Button
            disableElevation={true}
            className={classes.button}
            variant="contained"
            onClick={() => searchText.length > 3 && onSearch()}
          >
            Gugol Search
          </Button>
        </Grid>
      </Grid>
    </div>
  );
};
