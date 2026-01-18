/**
 * CSV Export Utility
 * Following Single Responsibility Principle - only handles CSV export
 */

/**
 * Converts an array of objects to CSV format
 */
export function convertToCSV(data: Record<string, any>[]): string {
  if (!data || data.length === 0) {
    return '';
  }

  // Get headers from the first object
  const headers = Object.keys(data[0]);
  
  // Create CSV header row
  const csvHeaders = headers.join(',');
  
  // Create CSV data rows
  const csvRows = data.map(row => {
    return headers.map(header => {
      const value = row[header];
      
      // Handle null/undefined
      if (value === null || value === undefined) {
        return '';
      }
      
      // Convert to string
      const stringValue = String(value);
      
      // Escape quotes and wrap in quotes if contains comma, newline, or quote
      if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      
      return stringValue;
    }).join(',');
  });
  
  // Combine headers and rows
  return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Downloads CSV data as a file
 */
export function downloadCSV(data: Record<string, any>[], filename?: string): void {
  const csv = convertToCSV(data);
  
  if (!csv) {
    console.error('No data to export');
    return;
  }
  
  // Create blob
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  
  // Create download link
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  // Generate filename with timestamp
  const timestamp = new Date().toISOString().split('T')[0];
  const finalFilename = filename || `sorgu-sonucu-${timestamp}.csv`;
  
  link.setAttribute('href', url);
  link.setAttribute('download', finalFilename);
  link.style.visibility = 'hidden';
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Cleanup
  URL.revokeObjectURL(url);
}
