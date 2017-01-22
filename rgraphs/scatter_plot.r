tx <- read.csv(file="transaction_info.csv",sep=",",head=TRUE)
png(filename = "bitcoin-fees.png",
    width = 2560, height = 1440, units = "px", pointsize = 12)
plot(tx$fee_rate,tx$conf_time, log="xy", yaxt="n", xaxt="n", pch = 20, cex=0.05)
marks <- c(0,60,600,3600,86400)
axis(2,at=marks,labels=marks)
xmarks <- c(1,5,10,20,100,300,1000,5000)
axis(1,at=xmarks,labels=xmarks)
