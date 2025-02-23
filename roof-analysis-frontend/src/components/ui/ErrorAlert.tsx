import React from 'react';

type ErrorAlertProps = {
  error?: string | null;
};

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error }) => {
  if (!error) return null;

  return (
    <div className="p-4 bg-red-100 text-red-700 rounded-md">
      {error}
    </div>
  );
};
