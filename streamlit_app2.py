import streamlit as st
import pandas as pd
import numpy as np
import os
import shutil
import subprocess
import sys

st.title("🎈Actuarial Governance Demo")
st.write("Credentials determine the run-setting permissions")
st.write("Actuarial modellers upload their model *.py and data into appropriate directories")
st.write("Centre of Excellence maintains access logins and model directories")


st.title("1: LOGIN sets access level")

# a file with the login credentials should be maintained by a senior officer
login_ids_df = pd.read_csv('loginIDs.csv')
# then loaded into a python dictionary
login_access_dict = dict(zip(login_ids_df['loginID'],login_ids_df['accessLevel']))

user_access_level = None
user_login_id = st.text_input("Enter LoginID:", key = "user_login_id")

if user_login_id:
    if user_login_id in login_access_dict:
        user_access_level = login_access_dict[user_login_id]
        st.success(f"LoginID is valid! Access Level: {login_access_dict[user_login_id]}")
    else:
        st.error("Invalid LoginID. Please try again.")

if user_access_level:
    st.title("2: check PASSWORD")
    login_pwd_df = pd.read_csv('passWord.csv')
    # load dictionary
    login_pwd_dict = dict(zip(login_pwd_df['passWord'],login_pwd_df['userName']))
    login_pwd = st.text_input("Enter password:", type = "password")
    #st.write("Password entered:",login_pwd)
    if login_pwd in login_pwd_dict:
        # we need to check if the loginID linked to the password is consistent
        #st.write(f"login: {user_login_id}")
        #st.write(f"pswd: {login_pwd_dict[login_pwd]}")
        if user_login_id == login_pwd_dict[login_pwd]:
            st.success("2A password valid, access approved")
            #st.session_state["login_pwd"] = ""
            #
            st.title("3: Run Process selection")
            st.write(f"your access level:{login_access_dict[user_login_id]}")
            RunType_df = pd.read_csv('LiabRuns.csv')
            #
            # start of function definition
            def get_access_array(access_level):
                 # filter the dataframe for the given access level
                 access_row = RunType_df[RunType_df['accessLevel'] == access_level]
                 #
                 # extract the boolean values for the products
                 if not access_row.empty:
                     access_array = access_row.iloc[0, 1:].values.astype(bool)
                     return access_array
                 else:
                     return None
            # end of function definition
            #
            # now use function
            access_array = get_access_array(user_access_level)
            if access_array is not None:
                st.success("found liabilities to process")
                # get source directory of the model PW code
                import csv
                sourcedir_array = []
                with open("defaults.csv", mode = "r") as file:
                    reader = csv.reader(file)
                    #read each row and place into our array
                    for row in reader:
                        sourcedir_array.append(str(row))
                    # end for
                if login_access_dict[user_login_id] == "snr301":
                    st.write("you have authority to change the source data directories")
                    count = 0
                    for sourcedir in sourcedir_array: 
                        # change directory if the admin wants to do so
                        sourcedir_array[count] = str(st.text_input(f"Directory {count + 1}:",str(sourcedir)))
                        count = count + 1
                    # end for
                else:
                    st.write("Check with your administrator for the process directories")
                    st.write("Ensure that your models and data are in the right directory")
                # end if
                st.title("4: select what to process")
                # start with an empty list to process
                processlist = []
                # runType is the integer mapping to sourcedir name, each directory holds only models for this run-setting
                runType = 0
                runDir = []
                # loop thru the entire source code and select only those with access permissions
                for sourcedir in sourcedir_array:
                    if access_array[runType]:
                        try:
                            # Ensure directory exists
                            # st.write(str(sourcedir))
                            os.makedirs(str(sourcedir), exist_ok = True)
                            
                            Liabmodel_array = []
                            for filename in os.listdir(str(sourcedir)):
                                full_file_name = os.path.join(str(sourcedir), filename)
                                # st.write(full_file_name)
                                if os.path.isfile(full_file_name):
                                    # st.write("appended to run setup")
                                    Liabmodel_array.append(filename)
                                # end if
                            st.success("source files found") #return True
                        except Exception as e:
                            st.error(f"Error in finding source directories: {e}")
                            # return False
                        # end of Try
                        # now the 
                        processlist.append(Liabmodel_array)
                        runDir.append(sourcedir) 
                    # end if
                    runType = runType + 1
                # end for
                count = 0
                this_run = []
                for this_array in processlist:
                    selected_items = st.multiselect(f"From:{sourcedir_array[count]}", this_array, key=f"uni_{count}")
                    if selected_items:
                        this_df = pd.DataFrame(selected_items, columns=['Selected Items'])
                        st.dataframe(this_df)
                    # end if
                    # after this the variable selected_items only contains selected prod liabs from UI/UX interface
                    this_run.append(selected_items)
                    # note that this_run is also a list and it is indexed in the order of the defaults.csv directory list
                    count = count + 1
                #
                st.write("5: once selected, initiate Pathwise run")
                if st.button("Process"):
                    count = 0
                    for this_array in this_run:
                         for filename in this_array:
                             PW_py_file = os.path.join(runDir[count], filename)
                             # this file can be run directly in the PW environment
                             st.write(f"initiate run selection: {count + 1}")
                             st.write(str(PW_py_file))
                             result = subprocess.run([sys.executable, PW_py_file], capture_output = True, text = True)
                             st.text(result.stdout)
                             
                         # end for this_array
                         count = count + 1
                    # end for this_run
                # end if

                #def copy_files(source_dir, destn_dir):
                #     try:
                #         # ensure destination directory exist
                #         os.makedirs(destn_dir, exist_ok = True)
                #         
                #         for filename in os.listdir(source_dir):
                #              full_file_name = os.path.join(source_dir, filename)
                #              if os.path.isfile(full_file_name):
                #                  shutil.copy(full_file_name, destn_dir)
                #                  #
                #              # end if
                #         # end for
                #         return True
                #     except Exception as e:
                #         st.error(f"Error: {e}")
                #         st.write("nothing to transfer")
                #         return False
                #     # end try
                # end def

            else:
                st.error("input error")      
            #

        else:
            st.error("Invalid password. Please try again.")
            #st.session_state["login_pwd"] = ""
            #
