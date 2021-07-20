import sqlite3
import MasterFileHandler

class sql:
    '''
    A class to handle the connection with Python and the SQL Lite Database
    '''


    def __init__(self):
        '''
        Initialise the object, get relevant configs, and to create the DB if not created
        '''
        # create File Handler Object and get relevant configs
        self.file_handler = MasterFileHandler.MasterFileHandler()
        self.sql_table_name = self.file_handler.table_name
        self.db_name = self.file_handler.db_name

        # Run code to create DB and table if not already created
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()

        # Check to see if table already exists
        check_table_exists_command = '''SELECT count(name) FROM sqlite_master 
                                        WHERE type='table' AND name='{}';'''.format(self.sql_table_name)
        cur.execute(check_table_exists_command)

        # If the table does not exist
        if cur.fetchone()[0] == 0: 
            create_table_command = '''CREATE TABLE {} (
                                      N TEXT NOT NULL,
                                      Lower_Limit TEXT NOT NULL,
                                      Upper_Limit TEXT NOT NULL,
                                      Ipv4 TEXT,
                                      PRIMARY KEY 
                                      (N, Lower_Limit, Upper_Limit)
                                      );'''.format(self.sql_table_name)
            cur.execute(create_table_command)
            connection.commit()
        connection.close()
    

    def insert_partitions_into_table(self, all_partitions):
        '''
        Take a list where for format of each element is of the format (N, Lower Limit, Upper Limit)
        The add a new row into the table for each element in the list
        '''
        connection = sqlite3.connect(self.db_name)
        connection.executemany('''INSERT into {} (N, Lower_Limit, Upper_Limit) 
                                  VALUES (?,?,?)'''.format(self.sql_table_name), all_partitions)
        connection.commit()
        connection.close()


    def remove_completed_row(self, N, Lower_Limit, Upper_Limit, ipv4):
        '''
        If a row has been completed with no solution, remove it from the table
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        delete_row_command = '''DELETE FROM {} WHERE N = '{}' AND 
                                Lower_Limit = '{}' AND 
                                Upper_Limit = '{}' 
                                AND Ipv4 = '{}';'''.format(self.sql_table_name, N, Lower_Limit, Upper_Limit, ipv4)
        cur.execute(delete_row_command)
        connection.commit()
        connection.close()

    
    # If a solution for N has been found you can remove all the rows realted to N
    def remove_completed_N(self, N):
        '''
        If a solution for N has been found you can remove all the rows realted to the solved N
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        delete_completed_rows_command = '''DELETE FROM {} WHERE N = '{}';'''.format(self.sql_table_name, N)
        cur.execute(delete_completed_rows_command)
        connection.commit()
        connection.close()
    
    
    def check_N_availability(self, N):
        '''
        Check to see if N is already in the DB or has already been solved
        Will return 0 if not in the DB and not already been solved
        '''

        # TODO: Check to see if N has already been solved

        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        check_N_command = '''SELECT COUNT(1) FROM {} WHERE N = '{}';'''.format(self.sql_table_name, N)
        cur.execute(check_N_command)
        count = cur.fetchone()[0]
        connection.close()
        return count


    def assign_client_to_row(self, ipv4):
        '''
        Assign an IP to a table row to show that a client is working on that number range
        Will return the N, Upper Limit and Lower Limit of the table row it has been assigned
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()

        # check to see if the IP has already been assigned, if so then resend that info
        check_ip_command = '''SELECT N, Lower_Limit, Upper_Limit FROM {} 
                              WHERE Ipv4 = '{}';'''.format(self.sql_table_name, ipv4)
        cur.execute(check_ip_command)
        assigned_row = cur.fetchone()
        
        # If no row is assigned
        if assigned_row == None:
            # Get 1st unworked row
            get_unworked_command = '''SELECT N, Lower_Limit, Upper_Limit FROM {} WHERE 
                                      Ipv4 IS NULL LIMIT 1;'''.format(self.sql_table_name)
            cur.execute(get_unworked_command)
            N, Lower_Limit, Upper_Limit = cur.fetchone()
            
            # assign that unworked row to the IP
            assign_client_command = '''UPDATE {} SET Ipv4 = '{}' 
                                       WHERE N = '{}' AND 
                                       Lower_Limit = '{}' AND 
                                       Upper_Limit = '{}';'''.format(self.sql_table_name, ipv4, N, Lower_Limit, Upper_Limit)
            cur.execute(assign_client_command)
        else:
            N, Lower_Limit, Upper_Limit = assigned_row
        
        connection.commit()
        connection.close()

        return N, Lower_Limit, Upper_Limit


    def get_ips(self):
        '''
        Get all the client IPs from the db
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        get_ips_command = '''SELECT Ipv4 FROM {} WHERE Ipv4 IS NOT NULL;'''.format(self.sql_table_name)
        cur.execute(get_ips_command)
        ips = cur.fetchall()
        connection.close()
        return ips


    def remove_ip_from_row(self, ipv4):
        '''
        Remove the IP assigned to a table row
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        remove_ip_command = '''UPDATE {} SET Ipv4 = NULL WHERE Ipv4 = '{}';'''.format(self.sql_table_name, ipv4)
        cur.execute(remove_ip_command)
        connection.commit()
        connection.close()


    def get_ip_working_on_N(self, N):
        '''
        Get the IPs for clients working on a completed N
        '''
        connection = sqlite3.connect(self.db_name)
        cur = connection.cursor()
        get_ip_command = '''SELECT Ipv4 from {} WHERE N = '{}' AND 
                            Ipv4 IS NOT NULL;'''.format(self.sql_table_name, N)
        cur.execute(get_ip_command)
        ips = cur.fetchall()
        connection.close()
        return ips

