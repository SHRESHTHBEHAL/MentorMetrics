import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { recordEvent } from '../utils/analytics';
import { useToast } from '../components/ui/ToastProvider';

import UploadBox from '../components/UploadBox';

const Upload = () => {
    const navigate = useNavigate();
    const { showSuccess, showError } = useToast();

    useEffect(() => {
        recordEvent('page_view', { page: 'upload' });
    }, []);

    return (
        <div className="py-12">
            <div className="text-center mb-12">
                <h2 className="text-5xl font-black uppercase tracking-tighter mb-4">Upload Session</h2>
                <p className="text-xl font-bold text-gray-600 uppercase max-w-2xl mx-auto border-l-4 border-black pl-4">
                    Upload your classroom recording to get started with the analysis.
                </p>
            </div>
            <UploadBox />
        </div>
    );
};

export default Upload;
