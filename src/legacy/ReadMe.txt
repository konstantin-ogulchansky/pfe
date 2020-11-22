
#########################################################################################################################################

During my internship, for each task I had, I wrote a python script, thats why you will find several python files
in the folder that I sent. you might find it difficult to use or to read because there are a lot of files
and I didn't put a lot of comments, Sorry for that ! 

Well, what I did now is, I collected the most important files and I tried to comment them. There are two folders;
one for the model implementation that has been done by Thibaud, and another folder for the graph study that I did.

The most important code is the one responsible on building and parsing the graph "graphBuilding.py" I used this code
each time I need to retrieve some data from the graph or to export some metrics or to draw the clusters, I tried to comment the role of
each function in it, you will only need to change the URL of the scopus json files and import the libraries and it will
work. you can change it of cou	rse depends on that tasks that you will have to do, you will find examples of how I used 
to use it in internship.zip. 
There are other important files like "MatrixP.py" to calculate the SBM matrix 
and "evolution_number_collab_labex_clusters.py" to study the evolution over time of the number of collaboration between LABEX Clusters....

To run these scripts you will need first json files thats are in Internship.zip to build the graph. Some scripts will need some other files that you will find attached in the folder codes/Graph study:

-politakibettersortedpartition2018.json : contains the partion of the graph computer science nice, 21 clusters with ids from 0 to 20
-politakibetterinteredges.json : contains the number of edges between all clusters combinations.
-politakibetterinterpub.json : contains the number of publications between all clusters combinations.
-politakibetterintraedges.json : Contains the number of edges inside each cluster.
-politakibetterintrapub.json : Contains the number of publications inside each cluster.



###########################################################################################################################################

I did my best to back to the code, refator it and write comments, I couldn't comment each script in Internship.zip (matter of time and I have a lot of stuff going on right now), but I did comment the most important parts.
If you need any more clarifications feel free to ask, I will be always happy to help ! 


