import matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
W,H=1080,1398
fig=plt.figure(figsize=(6.8,8.8),dpi=200); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
EC='#555555'; LC='#8a8a80'; T1='#222222'; T2='#555555'
def box(x0,y0,x1,y1,title,sub=None):
    ax.add_patch(FancyBboxPatch((x0+12,y0+12),x1-x0-24,y1-y0-24,boxstyle='round,pad=12,rounding_size=14',fc='white',ec=EC,lw=1.0))
    cx=(x0+x1)/2; cy=(y0+y1)/2
    if sub:
        ax.text(cx,cy-15,title,ha='center',va='center',fontsize=10.6,color=T1); ax.text(cx,cy+16,sub,ha='center',va='center',fontsize=9.0,color=T2)
    else: ax.text(cx,cy,title,ha='center',va='center',fontsize=10.6,color=T1)
def line(pts): ax.plot([p[0] for p in pts],[p[1] for p in pts],color=LC,lw=1.5,solid_capstyle='butt',solid_joinstyle='miter')
def arrow(x,y0,y1): ax.annotate('',xy=(x,y1),xytext=(x,y0),arrowprops=dict(arrowstyle='->',color=LC,lw=1.5,shrinkA=0,shrinkB=0,mutation_scale=13))
box(302,32,779,101,'Observational field study')
box(207,140,875,232,'Greater Accra, Ghana','4 abattoir-adjacent sites · 15 Jun–15 Jul 2025')
box(88,296,533,388,'Tyre-fuel sites (JM, TL)','Open-air · scrap tyre combustion'); box(549,296,994,388,'LPG-fuel sites (AM, AV)','Semi-enclosed · gas combustion')
box(143,452,938,544,'Ambient monitoring (06:00–18:00, 30 days per site)','PM₂.₅ · PM₁₀ · CO · SO₂ · VOCs · Temp · Humidity')
box(255,582,827,674,'Data processing','Hourly averages → quality control')
box(64,738,342,830,'Between-site','Mann–Whitney U'); box(398,738,676,830,'Co-variation','Spearman correlations'); box(737,738,1015,830,'Site & microclimate','LME models')
box(347,868,735,961,'Non-linear associations','Spline regression')
box(302,1034,779,1104,'Key results'); box(302,1142,779,1212,'Conclusion')
arrow(541,101,140)
line([(541,232),(541,264)]); line([(310,264),(772,264)]); arrow(310,264,296); arrow(772,264,296)
line([(310,388),(310,420),(772,420),(772,388)]); arrow(541,420,452)
arrow(541,544,582)
line([(541,674),(541,706)]); line([(207,706),(875,706)]); arrow(207,706,738); arrow(541,706,738); arrow(875,706,738)
arrow(537,830,868)
line([(203,830),(203,1002),(875,1002),(875,830)]); line([(537,961),(537,1002)]); arrow(541,1002,1034)
arrow(541,1104,1142)
fig.savefig('fig/image1.png'); 
from PIL import Image
im=Image.open('fig/image1.png'); print(im.size); im.thumbnail((800,1000)); im.convert('RGB').save('fig/flow_preview.jpg',quality=85)
