/**
 * API-specific type definitions
 * Following Interface Segregation Principle - separate API contracts
 */

import type { User, Query, SQLGenerationResponse, SQLExecutionResponse } from './index';

/**
 * Authentication API contracts
 */
export interface IAuthApi {
  login(email: string, password: string): Promise<{ success: boolean; user?: User; error?: string }>;
  register(email: string, password: string): Promise<{ success: boolean; user?: User; error?: string }>;
  logout(): Promise<{ success: boolean }>;
  getCurrentUser(): Promise<User>;
  resetPassword(email: string, password: string): Promise<{ success: boolean; message: string }>;
}

/**
 * Query API contracts
 */
export interface IQueryApi {
  generateSQL(question: string, history?: { role: string; content: string }[], sessionId?: string): Promise<SQLGenerationResponse>;
  generateSQLStream(
    question: string,
    history: { role: string; content: string }[],
    onToken: (token: string) => void,
    onMetadata: (metadata: any) => void,
    sessionId?: string
  ): Promise<void>;
  runSQL(sql: string, question?: string, sessionId?: string): Promise<SQLExecutionResponse>;
  saveQuery(question: string, sql_query: string, is_trained: boolean): Promise<{ success: boolean; query_id?: number; error?: string }>;
  getMyQueries(): Promise<{ success: boolean; queries?: Query[]; error?: string }>;
  deleteQuery(id: number): Promise<{ success: boolean; error?: string }>;
}

/**
 * Admin API contracts
 */
export interface IAdminApi {
  getUsers(): Promise<User[]>;
  updateUserRole(userId: number, role: string): Promise<{ success: boolean }>;
  getLiveDDL(): Promise<{ ddl: string }>;
  getSavedDDL(): Promise<{ id: number; ddl_content: string; created_at: string }>;
  trainDDL(ddl: string): Promise<{ success: boolean; message: string }>;
}

/**
 * Combined API interface
 */
export interface IApiClient extends IAuthApi, IQueryApi, IAdminApi { }
