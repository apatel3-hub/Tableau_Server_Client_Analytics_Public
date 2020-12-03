
#############################################################
## Tableau Server Client  ########
## Progamatically adding users from One site to Another Site
#############################################################

import tableauserverclient as TSC
import os
import pandas as pd

#  Connecting to Tableau Server
server = TSC.Server("Server Url")
server.use_server_version()
tableau_auth_sndbx = TSC.TableauAuth(
    "username/email", os.environ.get('Login Password'), "Site name/ environment_name")

tableau_auth = TSC.TableauAuth(
    "Username/email", os.environ.get('Login Password'))


request_option = TSC.RequestOptions()
request_option.pagesize = 100
endpoint = server.users



#list of projects you want to add
projects_to_add = ["Claims"]
# Create new project
with server.auth.sign_in(tableau_auth):
    for p in projects_to_add:
        new_project = TSC.ProjectItem(p)
        server.projects.create(new_project)

#get list of all the users from Sandbox
with server.auth.sign_in(tableau_auth_sndbx):
    all_users = list(TSC.Pager(endpoint, request_option))
    userlist = [user.name for user in all_users]
    user_role = [user.site_role for user in all_users]
    user_id = [user.id for user in all_users]
    print(userlist)
    print(len(userlist))   

#get list of all the users from Server Site
with server.auth.sign_in(tableau_auth_sndbx):
    all_users = list(TSC.Pager(endpoint, request_option))
    userlist = [user.name for user in all_users]
    user_role = [user.site_role for user in all_users]
    user_id = [user.id for user in all_users]
    print(userlist)
    print(len(userlist))

# create user
with server.auth.sign_in(tableau_auth):
    for u in userlist:
        try:
            newU = TSC.UserItem(u,'Viewer' ) #Keeping all of them viewers Server Admins will be recognized automatically
        # add the new user to the site
            newU = server.users.add(newU)
            print(newU.name, newU.site_role)
        except:
            pass



# print the names of the groups on the server
with server.auth.sign_in(tableau_auth_sndbx):
    all_groups, pagination_item = server.groups.get()
    group_list = [group.name for group in all_groups]
    print("\nThere are {} groups on site: ".format(
        pagination_item.total_available))
    print(group_list)

group_list.remove('All Users')

# Create a new groups in the new site

with server.auth.sign_in(tableau_auth):  #*Sign in to new site
    for g in group_list:                 #*this group list is from sandbox site   
        # create a new instance with the group name
        newgroup = TSC.GroupItem(g)
        # call the create method
        newgroup = server.groups.create(newgroup)


#range to iterate over number of groups to get users of each group

iter_groups = range(1,len(group_list))


group_user_names = []
group_names = []

with server.auth.sign_in(tableau_auth_sndbx):
    for r in iter_groups:
        all_groups, pagination_item = server.groups.get()
        mygroup =all_groups[r]
        # get the user information 
        pagination_item = server.groups.populate_users(mygroup)
        # creates the names of the users
        #groups_w_users = [(user.name, mygroup.name) for user in mygroup.users]
        for user in mygroup.users :
            group_user_names.append(user.name)
            group_names.append(mygroup.name) 

Group_name_users_df = pd.DataFrame(
    {'Group_users_sndbx': group_user_names,
     'Group_name_sndbx': group_names,
     })

Group_name_users_df.head(50)



#get list of all the users from new site specifically for User ID
with server.auth.sign_in(tableau_auth):
    all_users = list(TSC.Pager(endpoint, request_option))
    userlist_ns = [user.name for user in all_users]
    user_id_ns = [user.id for user in all_users]
    user_role_ns = [user.site_role for user in all_users]


User_name_id_df = pd.DataFrame(
    {'user_name_ns': userlist_ns,
     'user_id_ns': user_id_ns,
     'user_role' : user_role_ns
     })



final_groups_users_id_df = pd.merge(Group_name_users_df, User_name_id_df,
                             left_on='Group_users_sndbx', right_on='user_name_ns')

final_groups_users_id_df.head(50)

#groups in new site
with server.auth.sign_in(tableau_auth):
    all_groups, pagination_item = server.groups.get()
    group_list_ns = [group.name for group in all_groups]


group_list_ns.remove('All Users')

#Trying to add members to group

iter_groups_ns = range(1,len(group_list_ns))

with server.auth.sign_in(tableau_auth):
    for r in iter_groups_ns :
        all_groups, pagination_item = server.groups.get()
        mygroup = all_groups[r]
        groups_ns = (final_groups_users_id_df['Group_name_sndbx']).tolist()
        usersids_group_ns = (final_groups_users_id_df['user_id_ns']).tolist()
        for g,u in zip(groups_ns,usersids_group_ns):   
            try:
                if mygroup.name == g :
                    server.groups.add_user(mygroup, u )
            except:
                pass