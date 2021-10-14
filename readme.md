Assumptions :

1. At a given time, Data and Back Up folder can/cannot have same number and version of replicas depending on sequence of APIs triggered
2. addReplica API always  replicates from  replica-1 in /data , because replica-1 will always have latest version due to persistData default of 3 replicas and no parameter of replica in persistData
3. At a given time, replica-1,replica-2 and replica-3 can be different from other replica's in as persistData only allows to download in 3 replicas
4. Used Symmetric encryption
