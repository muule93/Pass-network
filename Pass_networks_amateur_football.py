from mplsoccer import Pitch, FontManager
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba

#reading raw data
data = pd.read_csv('passes_morahalom_balastya.csv', sep=';')
ids = data['Passer'].unique()
ids.sort()

#grouping passes between players, calculating avg positions, counting passes
average_locs_and_count = (data.groupby('Passer')
                          .agg({'X':['mean'], 'Y':['mean', 'count']}))
average_locs_and_count.columns = ['X', 'Y', 'count']
average_locs_and_count.insert(loc=0, column='id', value=ids)
passes_between = data[['Passer', 'Reciever']].value_counts().reset_index(name='count')
at_least_3_passes = passes_between[passes_between['count'] > 2].dropna()
#setting starting and ending positions of the lines
passes_between1 = at_least_3_passes.merge(average_locs_and_count, left_on='Passer', right_index=True)
average_locs_and_count.insert(loc=0, column='Reciever', value=ids)
passes_between1 = passes_between1.merge(average_locs_and_count, left_on='Reciever', right_index=True, suffixes=['', '_end'])

#calculating the line width and marker sizes
MAX_LINE_WIDTH = 6
MAX_MARKER_SIZE = 3500
average_locs_and_count['marker_size'] = (average_locs_and_count['count']
                                         / average_locs_and_count['count'].max() * MAX_MARKER_SIZE)
passes_between1['width'] = (passes_between1['count_x'] / passes_between1['count_x'].max() *
                           MAX_LINE_WIDTH)
#Set color to make the lines more transparent when fewer passes are made
MIN_TRANSPARENCY = 0.3
color = np.array(to_rgba('ghostwhite'))
color = np.tile(color, (len(passes_between1), 1))
c_transparency = passes_between1['count_x'] / passes_between1['count_x'].max()
c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
color[:, 3] = c_transparency

#plotting the pitch
pitch = Pitch(pitch_type='opta', pitch_color='#3a5a40', stripe=False, line_color='white')
fig, axs = pitch.grid(figheight=10, title_height=0.06, endnote_space=0,
                      axis=False,
                      title_space=0, grid_height=0.83, endnote_height=0.06)
fig.set_facecolor("#3a5a40")

pass_lines = pitch.lines(passes_between1.X, passes_between1.Y,
                          passes_between1.X_end, passes_between1.Y_end, lw=passes_between1.width,
                         color=color, zorder=1, ax=axs['pitch'])
pass_nodes = pitch.scatter(average_locs_and_count.X, average_locs_and_count.Y,
                           s=average_locs_and_count.marker_size,
                           color='#22312b', edgecolors='black', linewidth=1, alpha=1, ax=axs['pitch'])
#putting shirt numbers on the nodes
for index, row in average_locs_and_count.iterrows():
    pitch.annotate(row.name, xy=(row.X, row.Y), c='white', va='center',
                    ha='center', size=16, weight='bold', ax=axs['pitch'])

URL = 'https://raw.githubusercontent.com/google/fonts/main/apache/roboto/Roboto%5Bwdth,wght%5D.ttf'
robotto_regular = FontManager(URL)

#endnote and title
axs['endnote'].text(0.16839, 1, "Succesful passes from minutes 1' to 54'", color='#c7d5cc',
                    va='center', ha='left', fontsize=12,
                    fontproperties=robotto_regular.prop)
axs['title'].text(0.5, 0.7, 'Mórahalom VSE 0-2 KSE Balástya ', color='#c7d5cc',
                  va='center', ha='center', fontproperties=robotto_regular.prop, fontsize=24)
axs['title'].text(0.5, 0.18, 'Csongrád-Csanád Megye 1, September 24, 2022', color='#c7d5cc',
                  va='center', ha='center', fontproperties=robotto_regular.prop, fontsize=15)

plt.show()
