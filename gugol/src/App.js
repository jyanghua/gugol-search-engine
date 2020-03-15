import React from "react";
import CssBaseline from "@material-ui/core/CssBaseline";
import { Switch, Route } from "react-router-dom";

import { LandingPage } from "./Containers/LandingPage";
import { SearchingPage } from "./Containers/SearchingPage";

export const App = () => {
  return (
    <div>
      <CssBaseline />
      <Switch>
        <Route exact path="/" component={LandingPage} />
        <Route path="/search" component={SearchingPage} />
      </Switch>
    </div>
  );
};
