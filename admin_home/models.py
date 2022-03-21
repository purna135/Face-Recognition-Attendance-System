from django.db import models


class Branch ( models . Model ):
    branchname = models. CharField ( max_length= 10, primary_key= True)
    def __str__(self):
        return  self . branchname

class Student_Info ( models . Model ):
    First_Name = models . CharField ( max_length=20)
    Last_Name = models . CharField ( max_length=20)
    Registration_No = models . CharField ( max_length=16, primary_key=True)
    Branch = models . ForeignKey( Branch , on_delete= models. CASCADE)
    Email = models . EmailField ( max_length= 50 )
    Parents_Email = models . EmailField ( max_length= 50 )

    def __str__(self):
        return str(f'{self.First_Name} {self.Last_Name}')
