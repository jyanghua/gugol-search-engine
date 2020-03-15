import React from "react";
import { useHistory } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import OutlinedInput from "@material-ui/core/OutlinedInput";
import InputAdornment from "@material-ui/core/InputAdornment";
import SearchIcon from "@material-ui/icons/Search";
import Grid from "@material-ui/core/Grid";
import FormControl from "@material-ui/core/FormControl";

import logo from "../assets/gugol-90.png";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3, 0, 3, 2.8)
  },
  imgContainer: {
    display: "flex",
    cursor: "pointer",
    alignItems: "center"
  },
  img: {
    padding: theme.spacing(2)
  },
  searchContainer: {
    maxWidth: "630px",
    marginRight: theme.spacing(1.5),
    display: "flex",
    flex: 1
  },
  formControl: {
    flex: 1,
    marginLeft: theme.spacing(1)
  },
  withoutLabel: {
    marginTop: theme.spacing(3)
  },
  input: {
    height: "45px",
    flex: 1
  },
  icon: {
    cursor: "pointer"
  }
}));

export default function TopBar({ searchText, setSearchText, onSearch }) {
  const classes = useStyles();
  const history = useHistory();

  const handleChange = event => {
    setSearchText(event.target.value);
  };

  return (
    <Grid container className={classes.root}>
      <Grid
        item
        onClick={() => history.push("/")}
        className={classes.imgContainer}
      >
        <img src={logo} alt="Homepage Gugol" />
      </Grid>
      <Grid item className={classes.searchContainer}>
        <FormControl className={classes.formControl} variant="outlined">
          <form
            onSubmit={e => {
              e.preventDefault();
              onSearch();
            }}
          >
            <OutlinedInput
              className={classes.input}
              type="search"
              value={searchText}
              onChange={handleChange}
              fullWidth
              endAdornment={
                <InputAdornment
                  position="end"
                  onClick={onSearch}
                  className={classes.icon}
                >
                  <SearchIcon />
                </InputAdornment>
              }
            />
          </form>
        </FormControl>
      </Grid>
    </Grid>
  );
}
