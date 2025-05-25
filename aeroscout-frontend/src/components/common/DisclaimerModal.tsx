"use client";

import React, { useState, useEffect } from 'react';
import { legalService } from '../../services/legalService';

const DISCLAIMER_ACCEPTED_KEY = 'hasAcceptedGeneralDisclaimer';

interface DisclaimerModalProps {
  onClose: () => void;
  isOpenInitially: boolean;
}

const DisclaimerModal: React.FC<DisclaimerModalProps> = ({ onClose, isOpenInitially }) => {
  const [isOpen, setIsOpen] = useState(isOpenInitially);
  const [disclaimerText, setDisclaimerText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // 获取免责声明文本
  useEffect(() => {
    const fetchDisclaimerText = async () => {
      try {
        setIsLoading(true);
        const text = await legalService.getDisclaimerText();
        setDisclaimerText(text);
      } catch (error) {
        console.error('获取免责声明文本失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (isOpenInitially) {
      fetchDisclaimerText();
    }
  }, [isOpenInitially]);

  useEffect(() => {
    setIsOpen(isOpenInitially);
  }, [isOpenInitially]);

  const handleAccept = () => {
    try {
      localStorage.setItem(DISCLAIMER_ACCEPTED_KEY, 'true');
    } catch (error) {
      console.error('Failed to set disclaimer acceptance in localStorage:', error);
    }
    setIsOpen(false);
    onClose();
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '500px',
        width: '100%',
        textAlign: 'center'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '20px', fontSize: '1.5rem', color: '#333' }}>重要声明</h2>
        
        {isLoading ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <p>加载中...</p>
          </div>
        ) : (
          <div
            style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6', color: '#555' }}
            dangerouslySetInnerHTML={{ __html: disclaimerText }}
          />
        )}
        <button
          onClick={handleAccept}
          disabled={isLoading}
          style={{
            backgroundColor: isLoading ? '#cccccc' : '#007bff',
            color: 'white',
            border: 'none',
            padding: '12px 25px',
            borderRadius: '5px',
            cursor: isLoading ? 'default' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            transition: 'background-color 0.2s ease',
            marginTop: '20px'
          }}
          onMouseOver={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#0056b3')}
          onMouseOut={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#007bff')}
        >
          我已阅读并同意
        </button>
      </div>
    </div>
  );
};

export default DisclaimerModal;

// Helper function to check if disclaimer has been accepted
// This can be imported and used in other parts of the application
export const hasUserAcceptedDisclaimer = (): boolean => {
  if (typeof window === 'undefined') {
    return false; // Or true, depending on SSR behavior desired
  }
  try {
    return localStorage.getItem(DISCLAIMER_ACCEPTED_KEY) === 'true';
  } catch (error) {
    console.error('Failed to read disclaimer acceptance from localStorage:', error);
    return false; // Default to not accepted if error
  }
};