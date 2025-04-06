/**
 * API service for the Rahalah Trip Planning Assistant
 */
import axios from 'axios';
import { ChatResponse, Message } from '../types';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a chat message to the backend API
 * 
 * @param message - The user's message
 * @param conversationId - Optional conversation ID for context
 * @param history - Optional conversation history
 * @param mode - Optional explicit mode override
 * @returns The chat response from the API
 */
export const sendChatMessage = async (
  message: string,
  conversationId?: string | null,
  history?: Message[],
  mode?: 'flight' | 'hotel' | 'trip'
): Promise<ChatResponse> => {
  try {
    const response = await apiClient.post<ChatResponse>('/api/chat', {
      message,
      session_id: conversationId ?? "",
      history: history || [],
      mode,
    });
    
    // Backend now returns the correct structure, no transformation needed.
    return response.data;

  } catch (error) {
    console.error('Error sending chat message:', error);
    
    // Provide a graceful error response with more details
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx range
        const errorMessage = error.response.data?.detail || 
                             error.response.data?.message || 
                             `Server error: ${error.response.status}`;
        throw new Error(errorMessage);
      } else if (error.request) {
        // The request was made but no response was received
        throw new Error('No response received from server. Please check your connection.');
      }
    }
    
    // Generic error
    throw new Error(
      'Failed to send message. Please try again.'
    );
  }
};

export default apiClient;
