"""
Export Service - CSV export for leads, tasks, and threads.

Provides CSV generation with proper headers and data formatting.
"""

import csv
import io
import logging
from typing import List, Dict
from datetime import datetime

from services.crm_store import CRMStore
from services.inbox_store import get_inbox_store

logger = logging.getLogger(__name__)


def export_leads_csv() -> str:
    """
    Export leads to CSV format.
    
    Returns:
        CSV string with headers and lead data
    """
    try:
        crm = CRMStore()
        leads = crm.list_leads()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'ID', 'Name', 'Status', 'Phone', 'Source', 'Tags',
            'Value', 'Notes', 'Created', 'Updated'
        ])
        
        # Data rows
        for lead in leads:
            writer.writerow([
                lead.get('id', ''),
                lead.get('name', ''),
                lead.get('status', ''),
                lead.get('phone', ''),
                lead.get('source', ''),
                lead.get('tags', ''),
                lead.get('value', ''),
                lead.get('notes', ''),
                lead.get('created_at', ''),
                lead.get('updated_at', '')
            ])
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Export leads CSV error: {e}", exc_info=True)
        return "Error generating CSV"


def export_tasks_csv() -> str:
    """
    Export tasks to CSV format.
    
    Returns:
        CSV string with headers and task data
    """
    try:
        crm = CRMStore()
        tasks = crm.list_tasks()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'ID', 'Title', 'Type', 'Status', 'Completed',
            'Lead ID', 'Thread ID', 'Due At', 'Created'
        ])
        
        # Data rows
        for task in tasks:
            writer.writerow([
                task.get('id', ''),
                task.get('title', ''),
                task.get('task_type', ''),
                task.get('status', ''),
                'Yes' if task.get('completed') else 'No',
                task.get('lead_id', ''),
                task.get('thread_id', ''),
                task.get('due_at', ''),
                task.get('created_at', '')
            ])
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Export tasks CSV error: {e}", exc_info=True)
        return "Error generating CSV"


def export_threads_csv() -> str:
    """
    Export inbox threads to CSV format.
    
    Returns:
        CSV string with headers and thread data
    """
    try:
        store = get_inbox_store()
        threads = store.list_threads()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'ID', 'Title', 'Platform', 'Status',
            'Message Count', 'Last Message', 'Created'
        ])
        
        # Data rows
        for thread in threads:
            messages = store.list_messages(thread['thread_id'])
            
            writer.writerow([
                thread.get('thread_id', ''),
                thread.get('title', ''),
                thread.get('platform', ''),
                'active',  # status not in table
                len(messages),
                thread.get('updated_at', ''),
                thread.get('created_at', '')
            ])
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Export threads CSV error: {e}", exc_info=True)
        return "Error generating CSV"


def export_all_data_zip() -> bytes:
    """
    Export all data (leads, tasks, threads) as ZIP archive.
    
    Returns:
        ZIP file bytes containing 3 CSV files
    """
    try:
        import zipfile
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add leads CSV
            leads_csv = export_leads_csv()
            zip_file.writestr('leads.csv', leads_csv)
            
            # Add tasks CSV
            tasks_csv = export_tasks_csv()
            zip_file.writestr('tasks.csv', tasks_csv)
            
            # Add threads CSV
            threads_csv = export_threads_csv()
            zip_file.writestr('threads.csv', threads_csv)
        
        return zip_buffer.getvalue()
    
    except Exception as e:
        logger.error(f"Export ZIP error: {e}", exc_info=True)
        return b''
