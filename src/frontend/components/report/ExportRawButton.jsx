import React, { useState } from 'react';
import { Code, Download } from 'lucide-react';
import LoadingButton from '../ui/LoadingButton';
import { useToast } from '../ui/ToastProvider';
import { api } from '../../utils/api';

const ExportRawButton = ({ sessionId }) => {
    const [downloading, setDownloading] = useState(false);
    const { showSuccess, showError } = useToast();

    const handleDownload = async () => {
        setDownloading(true);
        try {
            const response = await api.get(`/download/raw/${sessionId}`, {
                responseType: 'blob',
            });

            const file = new Blob([response.data], { type: 'application/json' });
            const fileURL = URL.createObjectURL(file);
            const link = document.createElement('a');
            link.href = fileURL;
            link.download = `mentor-metrics-session-${sessionId}.json`;
            document.body.appendChild(link);
            link.click();

            document.body.removeChild(link);
            URL.revokeObjectURL(fileURL);

            showSuccess('Raw data exported successfully');
        } catch (err) {
            console.error('Export failed:', err);
            showError('Failed to export raw data');
        } finally {
            setDownloading(false);
        }
    };

    return (
        <LoadingButton
            onClick={handleDownload}
            isLoading={downloading}
            variant="outline"
            className="flex items-center text-xs text-gray-600 border-gray-300 hover:bg-gray-50"
            size="sm"
        >
            <Code className="h-3 w-3 mr-2" />
            Export Raw JSON
        </LoadingButton>
    );
};

export default ExportRawButton;
