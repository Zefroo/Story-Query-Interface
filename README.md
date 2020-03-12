# Story Query Interface
 An mock search enginer interface for querying the contents of stories.
---------------------------------
Purpose:

For this project, I built an index of words in a collection of short stories, contained in grimms.txt. The program create a dictionary structure in python that allows for the following queries of words in the stories and their location and line numbers: 

 DESCRIPTION --- COMMAND1|COMMAND2|...
    --------------------------------------------------------
    Stories with Single Word --- word1
    Stories containing word1 or word2 --- word1 or word2
    Stories containing word1 and word2 --- word1 word2 | word1 and word2
    Stories containing n words --- word1 word2 word3 . . . wordn
    Stories where word1 occurs more than x times --- word1 morethan x
    Stories where word1 occurs more than word2 --- word1 morethan word2 \n
    To quit the program ---qquit
    To print commands again --- hhelp'''


