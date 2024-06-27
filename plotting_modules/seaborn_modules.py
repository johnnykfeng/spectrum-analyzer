import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

tips = sns.load_dataset('tips')
print(tips.head())

# attend = sns.load_dataset("attention").query("subject <= 12")
# print(attend.head())    
grid = sns.FacetGrid(tips, col="smoker", row="sex",
                    #  col_wrap=4, 
                     height=3, # height of entire figure
                    #  ylim=(0, 10),
                     margin_titles=True)
grid.map(sns.scatterplot, "total_bill", "tip", color="#334488")
grid.figure.subplots_adjust(wspace=0.01, hspace=0.01)
grid.figure.tight_layout()

plt.show()
