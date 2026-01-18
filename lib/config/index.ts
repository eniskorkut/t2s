/**
 * Configuration management
 * Following Single Responsibility Principle - configuration concerns separated
 */

export interface AppConfig {
  apiBaseUrl: string;
  apiTimeout: number;
}

class ConfigManager {
  private config: AppConfig;

  constructor() {
    this.config = {
      apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8084',
      apiTimeout: 220000, // SQL oluşturma işlemleri uzun sürebilir
    };
  }

  getConfig(): AppConfig {
    return { ...this.config };
  }

  getApiBaseUrl(): string {
    return this.config.apiBaseUrl;
  }

  getApiTimeout(): number {
    return this.config.apiTimeout;
  }
}

// Singleton instance following Dependency Inversion Principle
export const configManager = new ConfigManager();
