import React from 'react';
import { FileQuestion } from 'lucide-react';
import Button from '../Button';

const EmptyState = ({
    title = "No data found",
    description = "There is nothing to display here yet.",
    actionLabel,
    onAction,
    icon: Icon = FileQuestion
}) => {
    return (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm border border-gray-200 px-4">
            <div className="flex justify-center mb-4">
                <div className="bg-gray-50 p-3 rounded-full">
                    <Icon className="h-8 w-8 text-gray-400" />
                </div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
            <p className="text-sm text-gray-500 max-w-sm mx-auto mb-6">{description}</p>
            {actionLabel && onAction && (
                <Button onClick={onAction} variant="primary">
                    {actionLabel}
                </Button>
            )}
        </div>
    );
};

export default EmptyState;
