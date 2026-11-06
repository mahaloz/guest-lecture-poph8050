



LineWidth=2
ErrorBarLineWidth=1
JitterSize=2

TextSize=.7
par(mfrow=c(3,1), mar=c(3,7,2,2), oma=c(2,2,2,2), las=1)
Colors=c("red", "red", "blue", "blue", "forestgreen", "forestgreen")
Shades=c("pink", "red", "lightblue1", "blue", "palegreen", "forestgreen")

LineTypes=c(3,1)
PchType=c(21,23)

YAxisOffsetA=8
YAxisOffsetB=8
XAxisOffset=2

LabelSize=1.5
TextLine=-1.2
LabelAdj=1.14

###########Figure 2A#########################

SOK_NonVax_675A =read.table("DataFor2A_v2.csv", sep=",", skip=6, header=TRUE, nrows=20)
SOK_HVT_675A =read.table("DataFor2A_v2.csv", sep=",", skip=32, header=TRUE, nrows=9)


SOK_NonVax_Md5 =read.table("DataFor2A_v2.csv", sep=",", skip=77, header=TRUE, nrows=8)
SOK_HVT_Md5 =read.table("DataFor2A_v2.csv", sep=",", skip=93, header=TRUE, nrows=7)


SOK_NonVax_595 =read.table("DataFor2A_v2.csv", sep=",", skip=47, header=TRUE, nrows=10)
SOK_HVT_595 =read.table("DataFor2A_v2.csv", sep=",", skip=64, header=TRUE, nrows=7)


SOK_List=list(SOK_NonVax_675A, SOK_HVT_675A, SOK_NonVax_Md5, SOK_HVT_Md5, SOK_NonVax_595, SOK_HVT_595)




plot(0,0, xlim=c(0,56), ylim=c(0,100), col=0, axes=FALSE, ylab="", xlab="")
mtext("Percent of", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=72.5)
mtext("experimentally", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=57.5)
mtext("infected birds", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=42.5)
mtext("alive", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=27.5)

mtext("Day post experimental infection", 1, line=XAxisOffset, las=1, cex=TextSize)

box()

axis(2, pretty(c(0,100)))
axis(1, seq(0,56, 7))

for (i in 1:2)
{
	for (h in 0:2)
	{	
		if (h*2+i ==4)
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])])+JitterSize, col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
		else
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])]), col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
	}
}

mtext("A", 2, line=TextLine, at=100*LabelAdj, cex=LabelSize)



















###########Figure 2C#########################

SOK_NonVax_675A =read.table("DataFor2C.csv", sep=",", skip=65, header=TRUE, nrows=9)
SOK_HVT_675A =read.table("DataFor2C.csv", sep=",", skip=80, header=TRUE, nrows=6)

SOK_NonVax_Md5 =read.table("DataFor2C.csv", sep=",", skip=5, header=TRUE, nrows=8)
SOK_HVT_Md5 =read.table("DataFor2C.csv", sep=",", skip=20, header=TRUE, nrows=7)

SOK_NonVax_595 =read.table("DataFor2C.csv", sep=",", skip=34, header=TRUE, nrows=10)
SOK_HVT_595 =read.table("DataFor2C.csv", sep=",", skip=51, header=TRUE, nrows=7)

SOK_List=list(SOK_NonVax_675A, SOK_HVT_675A, SOK_NonVax_Md5, SOK_HVT_Md5, SOK_NonVax_595, SOK_HVT_595)




plot(0,0, xlim=c(0,56), ylim=c(0,100), col=0, axes=FALSE, ylab="", xlab="")
mtext("Percent of", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=65)
mtext("sentinels", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=50)
mtext("MDV positive", 2, line=YAxisOffsetA, las=1, cex=TextSize, adj=0, at=35)

mtext("Day post experimental infection of co-housed birds", 1, line=XAxisOffset, las=1, cex=TextSize)

box()

axis(2, pretty(c(0,100)))
axis(1, seq(0,56, 7))

for (i in 1:2)
{
	for (h in 0:2)
	{	
		
		if (h*2+i ==3)
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])])-JitterSize, col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
		else
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])]), col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
		
	}
}

mtext("B", 2, line=TextLine, at=100*LabelAdj, cex=LabelSize)








###########Figure 2D#########################


SOK_NonVax_675A =read.table("DataFor2D_v2.csv", sep=",", skip=75, header=TRUE, nrows=5)
SOK_HVT_675A =read.table("DataFor2D_v2.csv", sep=",", skip=90, header=TRUE, nrows=7)

SOK_NonVax_Md5 =read.table("DataFor2D_v2.csv", sep=",", skip=42, header=TRUE, nrows=8)
SOK_HVT_Md5 =read.table("DataFor2D_v2.csv", sep=",", skip=59, header=TRUE, nrows=7)

SOK_NonVax_595 =read.table("DataFor2D_v2.csv", sep=",", skip=8, header=TRUE, nrows=10)
SOK_HVT_595 =read.table("DataFor2D_v2.csv", sep=",", skip=26, header=TRUE, nrows=7)

SOK_List=list(SOK_NonVax_675A, SOK_HVT_675A, SOK_NonVax_Md5, SOK_HVT_Md5, SOK_NonVax_595, SOK_HVT_595)


#for (i in 1:6)
#{
#	SOK_List[[i]]=SOK_List[[i]][,colSums(SOK_List[[i]]>0)]
#}

plot(0,0, xlim=c(0,56), ylim=c(0,100), col=0, axes=FALSE, ylab="", xlab="")
mtext("Percent of", 2, line=YAxisOffsetB, las=1, cex=TextSize, adj=0, at=57.5)
mtext("sentinels alive", 2, line=YAxisOffsetB, las=1, cex=TextSize, adj=0, at=42.5)
#mtext("alive", 2, line=YAxisOffsetB, las=1, cex=TextSize, adj=0, at=40)

mtext("Day post experimental infection of co-housed birds", 1, line=XAxisOffset, las=1, cex=TextSize)

box()

axis(2, pretty(c(0,100)))
axis(1, seq(0,56, 7))

for (i in 1:2)
{
	for (h in 0:2)
	{	
		
		if (h*2+i ==3)
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])])+JitterSize, col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
		else
		{
			lines(100* colMeans(SOK_List[[h*2+i]][,4:ncol(SOK_List[[h*2+i]])]), col=Colors[h*2+i], lty=LineTypes[i], lwd=LineWidth)
		}
		
	}
}

mtext("C", 2, line=TextLine, at=100*LabelAdj, cex=LabelSize)














