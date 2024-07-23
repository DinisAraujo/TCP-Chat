# TCP-Chat
Terminal TCP Chat using Python

Server commands:
* **/admin** nickname - Promote a User to Admin
* **/kick** nickname - Kick an Admin/User
* **/ban** nickname - Ban an Admin/User by IP
* **/unban** nickname - Unban an Admin/User (not implemented yet)
* **/list** admins | users | banned - See list of Admins, online Users or banned Users (not implemented yet)

Admin commands:
* **/kick** nickname - Kick a User
* **/ban** nickname - Ban a User by IP
* **/unban** nickname - Unban a User (not implemented yet)

User commands:
* **/nick** new_nickname - Change your nickname
* **/secret** other_user_nickname *message* - Send a private message to another User
* **/list** admins | users - See list of Admins or online Users (not implemented yet)

Note: Admins can use all User commands