import * as Sentry from '@sentry/browser';
import PropTypes from 'prop-types';
import React from 'react';

export interface ISentryBoundryProps {
    eventId?: string;
}

const FallbackUI = (props: ISentryBoundryProps) => (
    <>
        <h3>Check if there is an error on your Sentry app</h3>
        <button type="button" onClick={() => Sentry.showReportDialog({eventId: props.eventId})}>
            Report feedback
        </button>
    </>
);

FallbackUI.propTypes = {
    eventId: PropTypes.string,
};

FallbackUI.defaultProps = {
    eventId: '',
};

export interface IExampleBoundryProps {
    eventId?: string;
}

export interface ExampleBoundaryState {
    eventId?: string;
    hasError: boolean;
}

class ExampleBoundary extends React.Component<IExampleBoundryProps, ExampleBoundaryState> {
    static getDerivedStateFromError() {
        return {hasError: true};
    }

    constructor(props: IExampleBoundryProps) {
        super(props);
        this.state = {hasError: false};
    }

    componentDidCatch(error: any, errorInfo: {
        [key: string]: any;
    }) {
        Sentry.withScope((scope) => {
            scope.setExtras(errorInfo);
            const eventId = Sentry.captureException(error);
            this.setState({eventId});
        });
    }

    render() {
        const {eventId, hasError} = this.state;
        const {children} = this.props;

        // render fallback UI
        if (hasError) {
            return <FallbackUI eventId={eventId}/>;
        }

        // when there's not an error, render children untouched
        return children;
    }
}


export default ExampleBoundary;
