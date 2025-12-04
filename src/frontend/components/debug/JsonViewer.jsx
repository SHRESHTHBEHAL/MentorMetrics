import React from 'react';

const JsonViewer = ({ data }) => {
    if (!data) return <span className="text-gray-400 italic">No data</span>;

    const jsonString = JSON.stringify(data, null, 2);

    return (
        <pre className="bg-gray-900 text-green-400 p-4 rounded-md overflow-x-auto text-xs font-mono border border-gray-700 shadow-inner">
            <code>{jsonString}</code>
        </pre>
    );
};

export default JsonViewer;
