import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import forEach from "lodash/forEach";

const useStyles = makeStyles(theme => ({
  paper: {
    padding: theme.spacing(1.5),
    marginBottom: theme.spacing(2),
    marginRight: theme.spacing(1.5),
    maxWidth: "630px",
    textAlign: "left",
    fontFamily: "Arial",
    color: theme.palette.text.secondary
  },
  url: {
    color: "#3c4043",
    fontSize: 13
  },
  title: {
    color: "#1a0db2",
    fontSize: 19,
    lineHeight: 1.8,
    textDecoration: "none",
    "&:hover": {
      cursor: "pointer",
      textDecoration: "underline"
    }
  },
  snippet: {
    color: "#3c4043",
    fontSize: 15,
    lineHeight: 1.5,
    wordBreak: "break-word"
  }
}));

export const ListResult = ({ url, title, snippet, searchLemmatized }) => {
  const classes = useStyles();

  if (title === null) {
    title = url.slice(0, 59) + "...";
  } else if (title === "" && snippet !== null && snippet !== "") {
    title = snippet.slice(0, 59) + "...";
  } else if (title.length > 59) {
    title += "...";
  }

  if (snippet === null) {
    snippet = url;
  } else if (snippet === "" && title !== null && title !== "") {
    snippet = title.slice(0, 200) + "...";
  } else if (snippet !== null && snippet.length > 349) {
    snippet = snippet.slice(0, 200) + "...";
  }

  let shortUrl = url;

  if (url.length > 80) {
    shortUrl = url.slice(0, 75) + "...";
  }

  const formattedUrl = shortUrl.replace(/\//g, " › ");

  return (
    <Paper elevation={1} className={classes.paper}>
      <Typography className={classes.url}>{formattedUrl}</Typography>
      <Typography
        className={classes.title}
        onClick={() => (window.location.href = `//${url}`)}
      >
        {title}
      </Typography>
      <Typography className={classes.snippet}>
        {snippet.split(" ").map(word => {
          let isBold = false;
          forEach(searchLemmatized, lemmatized => {
            if (RegExp(`\\b${lemmatized}\\b`, "g").test(word.toLowerCase()))
              isBold = true;
          });
          return isBold ? <b key = {url}> {word}</b> : ` ${word}`;
        })}
      </Typography>
    </Paper>
  );
};
