import React from 'react';
import {hot} from 'react-hot-loader/root';
import SentryBoundary from "./utils/SentryBoundary";

// import SentryBoundary from './utils/SentryBoundary';

const App = () => (
    <SentryBoundary>
        <h1>Hello</h1>
    </SentryBoundary>
);

export default hot(App);
