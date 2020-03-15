import React from "react";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import OutlinedInput from "@material-ui/core/OutlinedInput";
import InputAdornment from "@material-ui/core/InputAdornment";
import FormControl from "@material-ui/core/FormControl";
import SearchIcon from "@material-ui/icons/Search";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    flex: 1,
    maxWidth: 500
  },
  margin: {
    margin: theme.spacing(1),
    flex: 1
  },
  withoutLabel: {
    marginTop: theme.spacing(3)
  }
}));

export default function SearchBar({ searchText, setSearchText, onSearch }) {
  const classes = useStyles();

  const handleChange = event => {
    setSearchText(event.target.value);
  };

  return (
    <div className={classes.root}>
      <FormControl
        className={clsx(classes.margin, classes.textField)}
        variant="outlined"
      >
        <form
          onSubmit={e => {
            e.preventDefault();
            searchText.length > 3 && onSearch();
          }}
        >
          <OutlinedInput
            type="search"
            value={searchText}
            onChange={handleChange}
            autoFocus={true}
            required={true}
            fullWidth
            startAdornment={
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            }
          />
        </form>
      </FormControl>
    </div>
  );
}
