import React from 'react';
import UploadBox from '../components/UploadBox';

const Upload = () => {
    return (
        <div className="py-12">
            <div className="text-center mb-12">
                <h2 className="text-3xl font-extrabold text-gray-900">Upload Session</h2>
                <p className="mt-4 text-lg text-gray-500">
                    Upload your classroom recording to get started with the analysis.
                </p>
            </div>
            <UploadBox />
        </div>
    );
};

export default Upload;
