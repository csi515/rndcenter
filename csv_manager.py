import pandas as pd
import os
from datetime import datetime
import logging

class CSVManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def read_csv(self, filename):
        """Read CSV file and return DataFrame"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(filepath):
                return pd.read_csv(filepath)
            else:
                return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error reading {filename}: {e}")
            return pd.DataFrame()
    
    def write_csv(self, filename, data):
        """Write DataFrame to CSV file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            logging.error(f"Error writing {filename}: {e}")
            return False
    
    def append_to_csv(self, filename, data):
        """Append data to existing CSV file"""
        existing_data = self.read_csv(filename)
        if isinstance(data, dict):
            data = [data]
        new_data = pd.DataFrame(data)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        return self.write_csv(filename, combined_data)
    
    def update_row(self, filename, index, data):
        """Update specific row in CSV file"""
        df = self.read_csv(filename)
        if not df.empty and index < len(df):
            for key, value in data.items():
                df.at[index, key] = value
            return self.write_csv(filename, df)
        return False
    
    def delete_row(self, filename, index):
        """Delete specific row from CSV file"""
        df = self.read_csv(filename)
        if not df.empty and index < len(df):
            df = df.drop(index).reset_index(drop=True)
            return self.write_csv(filename, df)
        return False
    
    def backup_data(self):
        """Create backup of all CSV files"""
        backup_dir = os.path.join(self.data_dir, 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                src = os.path.join(self.data_dir, filename)
                dst = os.path.join(backup_dir, f"{timestamp}_{filename}")
                try:
                    import shutil
                    shutil.copy2(src, dst)
                except Exception as e:
                    logging.error(f"Error backing up {filename}: {e}")

# Global instance
csv_manager = CSVManager()
