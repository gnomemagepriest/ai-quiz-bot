import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from './Login';
import UserProfile from './UserProfile';
import QuizCreator from './QuizCreator';

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/login" component={Login} />
        <Route path="/user" component={UserProfile} />
        <Route path="/">
          <QuizCreator />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
