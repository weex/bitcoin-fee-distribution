tx <- read.csv(file="transaction_info.csv",sep=",",head=TRUE)
plot(tx$fee_rate,tx$conf_blocks, log="xy", pch = 20, cex=0.05)
