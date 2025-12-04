import React, { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import LoadingButton from '../ui/LoadingButton';
import { useToast } from '../ui/ToastProvider';
import { api } from '../../utils/api';

const DownloadReportButton = ({ sessionId }) => {
    const [downloading, setDownloading] = useState(false);
    const { showSuccess, showError } = useToast();

    const handleDownload = async () => {
        setDownloading(true);
        try {
            const response = await api.get(`/download/report/${sessionId}`, {
                responseType: 'blob', // Important for binary data
            });

            const file = new Blob([response.data], { type: 'application/pdf' });

            const fileURL = URL.createObjectURL(file);
            const link = document.createElement('a');
            link.href = fileURL;
            link.download = `report-${sessionId}.pdf`;
            document.body.appendChild(link);
            link.click();

            document.body.removeChild(link);
            URL.revokeObjectURL(fileURL);

            showSuccess('Report downloaded successfully');
        } catch (err) {
            console.error('Download failed:', err);
            showError('Failed to download report');
        } finally {
            setDownloading(false);
        }
    };

    return (
        <LoadingButton
            onClick={handleDownload}
            isLoading={downloading}
            variant="outline"
            className="flex items-center"
        >
            <Download className="h-4 w-4 mr-2" />
            Download PDF
        </LoadingButton>
    );
};

export default DownloadReportButton;
