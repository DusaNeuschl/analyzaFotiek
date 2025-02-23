import React from 'react';

type SuccessAlertProps = {
  message?: string | null;
};

export const SuccessAlert: React.FC<SuccessAlertProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div className="p-4 bg-green-100 text-green-700 rounded-md">
      {message}
    </div>
  );
};
