



par(mfrow=c(3,1), mar=c(3,7,2,2), oma=c(2,5,2,2), las=1)


TextLine=-1.2
LabelAdj=1.14





LineWidth=2
ErrorBarLineWidth=1

TextSize=.7

LineTypes=c(3,1)
PchType=c(21,23)

YAxisOffset=10
XAxisOffset=2

LabelSize=1.5
#TextLine=0
#LabelAdj=1.1



Colors=c("forestgreen", "forestgreen", "blue", "blue", "red", "red")
Shades=c("palegreen", "forestgreen", "lightblue1", "blue", "pink", "red")



FT_NonVax_595	= read.table("DataForS2_v2.csv", sep=",", skip=32, header=TRUE, nrows=10)
FT_HVT_595		= read.table("DataForS2_v2.csv", sep=",", skip=48, header=TRUE, nrows=10)

FT_NonVax_Md5	= read.table("DataForS2_v2.csv", sep=",", skip=2, header=TRUE, nrows=8)
FT_HVT_Md5		= read.table("DataForS2_v2.csv", sep=",", skip=16, header=TRUE, nrows=10)

FT_NonVax_675A	= read.table("DataForS2_v2.csv", sep=",", skip=64, header=TRUE, nrows=10)
FT_HVT_675A		= read.table("DataForS2_v2.csv", sep=",", skip=80, header=TRUE, nrows=10)

FT_NonVax_595=FT_NonVax_595[,-1]
FT_HVT_595=FT_HVT_595[,-1]
FT_NonVax_Md5=FT_NonVax_Md5[,-1]
FT_HVT_Md5=FT_HVT_Md5[,-1]
FT_NonVax_675A=FT_NonVax_675A[,-1]
FT_HVT_675A=FT_HVT_675A[,-1]

DustSampleTimes=as.numeric(sub("X", "", colnames(FT_NonVax_595))[1:ncol(FT_NonVax_595)])


na_safe_mean=function(x)
{
	mean(x, na.rm=TRUE)
}
na_safe_sd=function(x)
{
	sd(x, na.rm=TRUE)
}
Count_feathers=function(x)
{
	sum(!is.na(x))
}


Means=matrix(,6, ncol(FT_NonVax_595)) 
SDs=matrix(,6, ncol(FT_NonVax_595))
Counts=matrix(,6, ncol(FT_NonVax_595))

Means[1,]=apply(FT_NonVax_595, 2, na_safe_mean)
Means[2,]=apply(FT_HVT_595, 2, na_safe_mean)
Means[3,]=apply(FT_NonVax_Md5, 2, na_safe_mean)
Means[4,]=apply(FT_HVT_Md5, 2, na_safe_mean)
Means[5,]=apply(FT_NonVax_675A, 2, na_safe_mean)
Means[6,]=apply(FT_HVT_675A, 2, na_safe_mean)

SDs[1,]=apply(FT_NonVax_595, 2, na_safe_sd)
SDs[2,]=apply(FT_HVT_595, 2, na_safe_sd)
SDs[3,]=apply(FT_NonVax_Md5, 2, na_safe_sd)
SDs[4,]=apply(FT_HVT_Md5, 2, na_safe_sd)
SDs[5,]=apply(FT_NonVax_675A, 2, na_safe_sd)
SDs[6,]=apply(FT_HVT_675A, 2, na_safe_sd)

Counts[1,]=apply(FT_NonVax_595, 2, Count_feathers)
Counts[2,]=apply(FT_HVT_595, 2, Count_feathers)
Counts[3,]=apply(FT_NonVax_Md5, 2, Count_feathers)
Counts[4,]=apply(FT_HVT_Md5, 2, Count_feathers)
Counts[5,]=apply(FT_NonVax_675A, 2, Count_feathers)
Counts[6,]=apply(FT_HVT_675A, 2, Count_feathers)


Means=Means
SEs=SDs/sqrt(Counts)
Upper=Means + SEs*qt(.975, Counts-1)
Lower=Means + SEs*qt(.025, Counts-1)




###################################


Strains=c("595", "Md5", "675A")

#par(mfrow=c(1,1), mar=c(2,2,1,1), oma=c(4,8,2,2), las=1)

YLabAdj=0.5*3
YLabCenter=4.5

#for (h in 0:2)
{
	plot(1,1, xlim=c(0,56), ylim=c(0,9), col=0, axes=FALSE, ylab="", xlab="")
	box()
	
#	if (h==2)
	{
		mtext("Mean MDV", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+2.5*YLabAdj)
		mtext("concentration in", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+1.5*YLabAdj)
		mtext("feather follicles", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+0.5*YLabAdj)
		mtext("of experimentally", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter-0.5*YLabAdj)
		mtext("infected birds", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter-1.5*YLabAdj)
		mtext(expression(paste("(vcn/", 10^4, "cells)", sep="")), 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter-2.5*YLabAdj)
	}

#	if (h>2)
	{
		mtext("Day post experimental infection ", 1, line=XAxisOffset, las=1, cex=TextSize)
	}
	
#	mtext(Strains[h+1], 2, at=8.5, adj=0, line=-.3)
	
	axis(1, seq(0,56, 7))
	
	y <- 0:8
	aty <- axTicks(2)
	labels <- sapply(aty,function(i)
					 as.expression(bquote(10^ .(i)))
					 )
	axis(2,at=aty,labels=labels, las=1)
	
	
	
	for (h in 0:2)
	{
		for (i in 1:2)
		{
			
			segments(DustSampleTimes, as.numeric(Lower[h*2+i,]), DustSampleTimes, as.numeric(Upper[h*2+i,]), col=Colors[h*2+i], lwd=ErrorBarLineWidth)		
			
			lines(DustSampleTimes, as.numeric(Means[h*2+i,]), col=Colors[h*2+i], lty=LineTypes[i], lwd=ErrorBarLineWidth)
			points(DustSampleTimes, as.numeric(Means[h*2+i,]), col=Colors[h*2+i], pch=PchType[i], bg=Shades[h*2+i])
			
			if (h==2)
			{
				if(i==2)
				{
					lines(DustSampleTimes[c(7,9)], as.numeric(Means[h*2+i,c(7,9)]), col=Colors[h*2+i], lty=LineTypes[i], lwd=ErrorBarLineWidth)
				}
			}
		}
	}
	
}
mtext("A", 2, line=TextLine, at=9*LabelAdj, cex=LabelSize)







################Panel B############


Colors=c("red", "red", "blue", "blue", "forestgreen", "forestgreen")
Shades=c("pink", "red", "lightblue1", "blue", "palegreen", "forestgreen")


NonVax_675A		=read.table("DataFor2B.csv", sep=",", skip=25, header=TRUE, nrows=3)
HVT_675A		=read.table("DataFor2B.csv", sep=",", skip=31, header=TRUE, nrows=3)

NonVax_Md5		=read.table("DataFor2B.csv", sep=",", skip=14, header=TRUE, nrows=3)
HVT_Md5			=read.table("DataFor2B.csv", sep=",", skip=20, header=TRUE, nrows=3)

NonVax_595		=read.table("DataFor2B.csv", sep=",", skip=2, header=TRUE, nrows=3)
HVT_595			=read.table("DataFor2B.csv", sep=",", skip=8, header=TRUE, nrows=3)


DustSampleTimes=as.numeric(sub("X", "", colnames(NonVax_675A))[2:15])






VCN_matrix=rep(NA, 6*max(DustSampleTimes)*3)
dim(VCN_matrix)=c(6,max(DustSampleTimes),3)

VCN_matrix[1,DustSampleTimes,]=t(NonVax_675A[,2:15])
VCN_matrix[2,DustSampleTimes,]=t(HVT_675A[,2:15])

VCN_matrix[3,DustSampleTimes,]=t(NonVax_Md5[,2:15])
VCN_matrix[4,DustSampleTimes,]=t(HVT_Md5[,2:15])

VCN_matrix[5,DustSampleTimes,]=t(NonVax_595[,2:15])
VCN_matrix[6,DustSampleTimes,]=t(HVT_595[,2:15])


TempFunc=function(x)
{
	sum(!is.na(x))
}

NA_Safe_mean=function(x)
{
	mean(x, na.rm=TRUE)
}

NA_Safe_sd=function(x)
{
	sd(x, na.rm=TRUE)
}

c_4=c(NA, NA, sqrt(2/pi), sqrt(pi)/2, 2*sqrt(2/(3*pi)), 3/4*sqrt(pi/2), 8/3*sqrt(2/(5*pi)), 5*sqrt(3*pi)/16, 16/5*sqrt(2/(7*pi)), 35*sqrt(pi)/64, 128*sqrt(2/pi)/105)

VCN_matrix_count=apply(log(VCN_matrix), c(1,2), TempFunc)
VCN_matrix_sd=apply(log(VCN_matrix), c(1,2), NA_Safe_sd)/c_4[VCN_matrix_count+1]
VCN_matrix_mean=apply(log(VCN_matrix), c(1,2), NA_Safe_mean)


StandardDeviation=mean(VCN_matrix_sd, na.rm=TRUE)




plot(1,1, xlim=c(0,55), ylim=c(0,5.5), col=0, axes=FALSE, ylab="", xlab="")
box()



YLabAdj=0.305556*3
YLabCenter=2.75
		




mtext("Mean MDV", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+1*YLabAdj)
mtext("concentration", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+0*YLabAdj)
mtext(expression(paste("(vcn/", mu, "g dust)", sep="")), 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter-1*YLabAdj)

mtext("Day post experimental infection", 1, line=XAxisOffset, las=1, cex=TextSize)

axis(1, seq(0,56, 7))

y <- 0:7
aty <- axTicks(2)
labels <- sapply(aty,function(i)
as.expression(bquote(10^ .(i)))
)
axis(2,at=aty,labels=labels)


for (h in 2:0)
{
	for (i in 1:2)
	{
		
		MeanSD=mean(VCN_matrix_sd, na.rm=TRUE)
		SE=MeanSD/sqrt(VCN_matrix_count)
		
		segments(DustSampleTimes, log10(exp(VCN_matrix_mean[h*2+i,DustSampleTimes]-2*SE[h*2+i,DustSampleTimes])), DustSampleTimes, log10(exp(VCN_matrix_mean[h*2+i,DustSampleTimes]+2*SE[h*2+i,DustSampleTimes])), col=Colors[h*2+i], lwd=ErrorBarLineWidth)		
		
		lines(DustSampleTimes, log10(exp(VCN_matrix_mean[h*2+i,DustSampleTimes])), col=Colors[h*2+i], lty=LineTypes[i], lwd=ErrorBarLineWidth)
		points(DustSampleTimes, log10(exp(VCN_matrix_mean[h*2+i,DustSampleTimes])), col=Colors[h*2+i], pch=PchType[i], bg=Shades[h*2+i])
		
	}
}

lines(c(25,31), log10(exp(VCN_matrix_mean[2,c(25,31)])), col=Colors[2], lty=LineTypes[2], lwd=ErrorBarLineWidth)
mtext("B", 2, line=TextLine, at=5.5*LabelAdj, cex=LabelSize)





















Colors=c("red", "red", "blue", "blue", "forestgreen", "forestgreen")
Shades=c("pink", "red", "lightblue1", "blue", "palegreen", "forestgreen")


###########Figure 2A#########################

SOK_NonVax_675A =read.table("DataFor2A.csv", sep=",", skip=6, header=TRUE, nrows=10)
SOK_HVT_675A =read.table("DataFor2A.csv", sep=",", skip=23, header=TRUE, nrows=9)


SOK_NonVax_Md5 =read.table("DataFor2A.csv", sep=",", skip=68, header=TRUE, nrows=8)
SOK_HVT_Md5 =read.table("DataFor2A.csv", sep=",", skip=84, header=TRUE, nrows=7)


SOK_NonVax_595 =read.table("DataFor2A.csv", sep=",", skip=38, header=TRUE, nrows=10)
SOK_HVT_595 =read.table("DataFor2A.csv", sep=",", skip=55, header=TRUE, nrows=7)


SOK_List=list(SOK_NonVax_675A, SOK_HVT_675A, SOK_NonVax_Md5, SOK_HVT_Md5, SOK_NonVax_595, SOK_HVT_595)


FractionAlive_matrix=matrix(0,6,55)

for (i in 1:length(SOK_List))
{
	FractionAlive_matrix[i,1:(ncol(SOK_List[[i]])-3)]=colMeans(SOK_List[[i]][4:ncol(SOK_List[[i]])])
}



###########Figure 2B#########################


NonVax_675A		=read.table("DataFor2B.csv", sep=",", skip=25, header=TRUE, nrows=3)
HVT_675A		=read.table("DataFor2B.csv", sep=",", skip=31, header=TRUE, nrows=3)

NonVax_Md5		=read.table("DataFor2B.csv", sep=",", skip=14, header=TRUE, nrows=3)
HVT_Md5			=read.table("DataFor2B.csv", sep=",", skip=20, header=TRUE, nrows=3)

NonVax_595		=read.table("DataFor2B.csv", sep=",", skip=2, header=TRUE, nrows=3)
HVT_595			=read.table("DataFor2B.csv", sep=",", skip=8, header=TRUE, nrows=3)


DustSampleTimes=as.numeric(sub("X", "", colnames(NonVax_675A))[2:15])


NonVax_Md5_Corrector =read.table("DataFor2Trumpet.csv", sep=",", skip=52, header=FALSE, nrows=2, comment="")
NonVax_Md5_Corrector=NonVax_Md5_Corrector[4:ncol(NonVax_Md5_Corrector)]

HVT_Md5_Corrector =read.table("DataFor2Trumpet.csv", sep=",", skip=68, header=FALSE, nrows=2, comment="")
HVT_Md5_Corrector=HVT_Md5_Corrector[4:ncol(HVT_Md5_Corrector)]

NonVax_595_Corrector =read.table("DataFor2Trumpet.csv", sep=",", skip=20, header=FALSE, nrows=2, comment="")
NonVax_595_Corrector=NonVax_595_Corrector[4:ncol(NonVax_595_Corrector)]

HVT_595_Corrector =read.table("DataFor2Trumpet.csv", sep=",", skip=35, header=FALSE, nrows=2, comment="")
HVT_595_Corrector=HVT_595_Corrector[4:ncol(HVT_595_Corrector)]

VCN_matrix=rep(NA, 6*55*3)
dim(VCN_matrix)=c(6,55,3)

VCN_matrix[1,DustSampleTimes,]=t(NonVax_675A[,2:15])
VCN_matrix[2,DustSampleTimes,]=t(HVT_675A[,2:15])

VCN_matrix[3,DustSampleTimes,]=t(NonVax_Md5[,2:15])
VCN_matrix[4,DustSampleTimes,]=t(HVT_Md5[,2:15])

VCN_matrix[5,DustSampleTimes,]=t(NonVax_595[,2:15])
VCN_matrix[6,DustSampleTimes,]=t(HVT_595[,2:15])




AssumeNoSentinelShedding=TRUE
AssumeSentinelSheddingSameAsExp=FALSE
AssumeSentinelSheddingGreaterThanExp=FALSE

if (AssumeNoSentinelShedding==TRUE)
{
	Corrector=matrix(1,6,55)
	
	Corrector[3,]=unlist(c((NonVax_Md5_Corrector[1,])/(NonVax_Md5_Corrector[1,]-NonVax_Md5_Corrector[2,]), 1,1))
	Corrector[4,]=unlist(c((HVT_Md5_Corrector[1,])/(HVT_Md5_Corrector[1,]-HVT_Md5_Corrector[2,]),1,1))
	Corrector[5,]=unlist(c((NonVax_595_Corrector[1,])/(NonVax_595_Corrector[1,]-NonVax_595_Corrector[2,]),1,1))
	Corrector[6,]=unlist(c((HVT_595_Corrector[1,])/(HVT_595_Corrector[1,]-HVT_595_Corrector[2,]),1,1))	
	
	Corrector[is.na(Corrector)]=1
	Corrector[Corrector>1e10]=1e10
}

if (AssumeSentinelSheddingSameAsExp==TRUE)
{
	Corrector=matrix(1,6,55)
}

if (AssumeSentinelSheddingSameAsExp==TRUE)
{
##	Assume ten fold more shedding from sentinels
	Corrector=matrix(1,6,55)
	
	Corrector[3,]=unlist(c((NonVax_Md5_Corrector[1,])/(NonVax_Md5_Corrector[1,]-NonVax_Md5_Corrector[2,]), 1,1))
	Corrector[4,]=unlist(c((HVT_Md5_Corrector[1,])/(HVT_Md5_Corrector[1,]-HVT_Md5_Corrector[2,]),1,1))
	Corrector[5,]=unlist(c((NonVax_595_Corrector[1,])/(NonVax_595_Corrector[1,]-NonVax_595_Corrector[2,]),1,1))
	Corrector[6,]=unlist(c((HVT_595_Corrector[1,])/(HVT_595_Corrector[1,]-HVT_595_Corrector[2,]),1,1))	
	
	Corrector[is.na(Corrector)]=1
	Corrector[Corrector>1e10]=1e10
}

VCN_matrix[,,1]=VCN_matrix[,,1]*Corrector
VCN_matrix[,,2]=VCN_matrix[,,2]*Corrector
VCN_matrix[,,3]=VCN_matrix[,,3]*Corrector


TempFunc=function(x)
{
	sum(!is.na(x))
}

NA_Safe_mean=function(x)
{
	mean(x, na.rm=TRUE)
}

NA_Safe_sd=function(x)
{
	sd(x, na.rm=TRUE)
}

c_4=c(NA, NA, sqrt(2/pi), sqrt(pi)/2, 2*sqrt(2/(3*pi)), 3/4*sqrt(pi/2), 8/3*sqrt(2/(5*pi)), 5*sqrt(3*pi)/16, 16/5*sqrt(2/(7*pi)), 35*sqrt(pi)/64, 128*sqrt(2/pi)/105)

VCN_matrix_count=apply(log(VCN_matrix), c(1,2), TempFunc)
VCN_matrix_sd=apply(log(VCN_matrix), c(1,2), NA_Safe_sd)/c_4[VCN_matrix_count+1]
VCN_matrix_mean=apply(log(VCN_matrix), c(1,2), NA_Safe_mean)


StandardDeviation=mean(VCN_matrix_sd, na.rm=TRUE)

DustSampleList=list()
for (i in 1:6)
{
	DustSampleList[[i]]=which(!is.na(VCN_matrix_mean[i,]))
}



RightSheddingRate=TRUE
if (RightSheddingRate==TRUE)
{
###If we use right datapoint to estimate shedding rate
	
	for (i in 1:6)							#For all six treatments
	{
		VCN_matrix_mean[i,55]=VCN_matrix_mean[i,max(which(VCN_matrix_mean[i,]>0))]		
#		VCN_matrix_mean[i,55]=max(VCN_matrix_mean[i,], na.rm=TRUE)		
	}
	
	VCN_matrix_mean[,55][is.na(VCN_matrix_mean[,55])]=0
	for (i in 54:1)
	{
		VCN_matrix_mean[,i][is.na(VCN_matrix_mean[,i])]=VCN_matrix_mean[,i+1][is.na(VCN_matrix_mean[,i])]
	}
}

if (RightSheddingRate==FALSE)
{
###If we use right datapoint to estimate shedding rate
	VCN_matrix_mean[,1][is.na(VCN_matrix_mean[,1])]=0
	for (i in 2:55)
	{
		VCN_matrix_mean[,i][is.na(VCN_matrix_mean[,i])]=VCN_matrix_mean[,i-1][is.na(VCN_matrix_mean[,i])]
	}
}



t=c(10:64)

FinishingDay=64
P_FD=-FinishingDay^1.64*log((206-10.8)/368)
DustShed=1000*(368 * exp(-P_FD/t^1.64) +10.8)		#From Atkins paper using finishing day 64









################################################################################
################################################################################
################################################################################


YLabAdj=0.4444*3
YLabCenter=8

plot(1,1, xlim=c(0,56), ylim=c(4,12), col=0, axes=FALSE, xlab="", ylab="")
box()
y <- 4:12
aty <- axTicks(2)
labels <- sapply(aty,function(i)
as.expression(bquote(10^ .(i)))
)
axis(2,at=aty,labels=labels)
axis(1, seq(0,56, 7))

mtext("Day post experimental infection", 1, line=XAxisOffset, las=1, cex=TextSize)

mtext("Cumulative viral", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+1*YLabAdj)
mtext("genomes shed", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter+0*YLabAdj)
mtext("from an infection", 2, line=YAxisOffset, las=1, cex=TextSize, adj=0, at=YLabCenter-1*YLabAdj)


StopTime=53
for (h in 2:0)
{
	
	
	NumberOfSimulations=10000
	
	for (i in 2:1)
	{			
		
		TempMean=VCN_matrix_mean[h*2+i,]	
		TempSD=VCN_matrix_sd[h*2+i,]
		
		SameSD=TRUE					#Standard deviation caused by measurement error is assumed identical across dust samples
		if (SameSD==TRUE)
		{
			TempSD=rep(mean(VCN_matrix_sd, na.rm=TRUE), StopTime)
		}
		
		BootstrapMatrix=matrix(,NumberOfSimulations, StopTime)
		
		Breaks=c(1,DustSampleList[[h*2+i]], StopTime+1)
		
		for (k in 1:NumberOfSimulations)
		{
			
			
			IndividualBirdEffect=rep(0, 10)
			TempFocalBirds=c(1:10)
			
			NewTempMean=numeric(length(TempMean))
			for (m in 1:length(TempMean))
			{
#				Culled=length(which(WellfareCulled[[h*2+i]]==m))
				Culled=0
				if (Culled>0)
				{
					IndividualBirdEffect=IndividualBirdEffect[-sample(length(IndividualBirdEffect), Culled)]
				}
				if (length(FractionAlive_matrix[h*2+i,m]*length(TempFocalBirds))>0)
				{
					NewTempMean[m]=log(mean(exp(TempMean[m]+IndividualBirdEffect[1:(FractionAlive_matrix[h*2+i,m]*length(TempFocalBirds))])))
				}
				else
				{
					NewTempMean[m]=NewTempMean[m-1]
				}
			}
			
			
			
			for (j in 1:(length(Breaks)-1))
			{
				TimeRange=Breaks[j]:(Breaks[j+1]-1)
				BootstrapMatrix[k, TimeRange]=DustShed[TimeRange]*FractionAlive_matrix[h*2+i,TimeRange]*exp(rnorm(1, NewTempMean[TimeRange[1]], TempSD[TimeRange[1]]))
				
			}
		}
		
		CumulativeBootstrapMatrix=log10(apply(BootstrapMatrix, 1, cumsum))
		
		MonitorRange=c(min(DustSampleList[[h*2+i]]):StopTime)
		
		Median=numeric(StopTime)
		for (j in 1:StopTime)
		{
			Median[j]=quantile(CumulativeBootstrapMatrix[j,],p=.5)
		}
		
		
		Time=c(1:StopTime)
		
		Lower=numeric(StopTime)
		Upper=numeric(StopTime)
		for (j in 1:StopTime)
		{
			Lower[j]=quantile(CumulativeBootstrapMatrix[j,], p=.025)
			Upper[j]=quantile(CumulativeBootstrapMatrix[j,], p=.975)
		}
		
		if (i==1)
		{
			polygon(c(Time[MonitorRange], rev(Time[MonitorRange])), c(Upper[MonitorRange], rev(Lower[MonitorRange])), col = Shades[h*2+i], border = NA)
		}
		else
		{
			polygon(c(Time[MonitorRange], rev(Time[MonitorRange])), c(Upper[MonitorRange], rev(Lower[MonitorRange])), col = Shades[h*2+i], border = NA)
		}
		lines(Time[MonitorRange], Lower[MonitorRange], col=Colors[h*2+i], lty=LineTypes[i], lwd=ErrorBarLineWidth)
		lines(Time[MonitorRange], Upper[MonitorRange], col=Colors[h*2+i], lty=LineTypes[i], lwd=ErrorBarLineWidth)
		
		if (i==1)
		{
			TempStor1=CumulativeBootstrapMatrix[StopTime,]
		}
		if (i==2)
		{
			TempStor2=CumulativeBootstrapMatrix[StopTime,]
		}
		
		TempLower=numeric(StopTime)
		TempUpper=numeric(StopTime)
		for (j in 1:StopTime)
		{
			TempLower[j]=quantile(CumulativeBootstrapMatrix[j,], p=.025)
			TempUpper[j]=quantile(CumulativeBootstrapMatrix[j,], p=.975)
		}
		
	}
	
	mtext("C", 2, line=TextLine, at=12+(8*LabelAdj-8), cex=LabelSize)

	
}








