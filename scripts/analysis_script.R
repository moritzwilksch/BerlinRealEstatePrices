library(arrow)
library(dplyr)
library(ggplot2)
library(lme4)
library(lattice)

dfrent = read_parquet("data/dfrent.parquet")
dfbuy = read_parquet("data/dfbuy.parquet")

#rent_cutoff = quantile(dfrent$price, 0.99)
#buy_cutoff = quantile(dfbuy$price, 0.99)
#dfrent = dfrent %>% filter(price <= rent_cutoff)
#dfbuy = dfbuy %>% filter(price <= buy_cutoff)

# square_meters outliers
dfrent_cutoff = quantile(dfrent$square_meters, 0.999, na.rm=TRUE)
dfbuy_cutoff = quantile(dfbuy$square_meters, 0.999, na.rm = TRUE)

nrow(dfrent %>% filter(square_meters > dfrent_cutoff))  # removes 21 outliers
nrow(dfbuy %>% filter(square_meters > dfbuy_cutoff))  # removes 32 outliers

dfrent = dfrent %>% filter(square_meters <= dfrent_cutoff)
dfbuy = dfbuy %>% filter(square_meters <= dfbuy_cutoff)

# Rent prices
ggplot(data=dfrent, aes(x=log(price))) + geom_histogram(bins=60) + theme_bw()  # some zeros

# Buy prices
ggplot(data=dfbuy, aes(x=price)) + geom_histogram(bins=60) + theme_bw() # many zeros

################### RENTAL UNITS ###################
################### EDA ###################

# price by sqm
ggplot(data=dfrent, aes(x=square_meters, y=price, color=private_offer)) + geom_point(alpha=0.1) + theme_bw() + geom_smooth(method='lm')

# rooms * sqm interaction
# same direction, but different slopes per n_rooms
ggplot(data=dfrent, aes(x=square_meters, y=price)) + geom_point(alpha=0.5) + geom_smooth(method="lm") + facet_grid(~ rooms)




################### Modelling - Non-hierarchical ###################
# all mean effects
model0 = lm(log(price) ~ object_type + private_offer + rooms + square_meters, data=dfrent)
summary(model0)
plot(model0)


plot(model0, which=4) # high cooks dist for 21527, 19074, 19565

high_dist = c(21527, 19074, 19565)
problematic = c(9841, 13702, 16558)

# refit
leverage_removed = dfrent[-high_dist, ]
leverage_removed = leverage_removed[-problematic, ]

write_parquet(leverage_removed, "data/intermediaries/leverage_removed.parquet")
model0 = lm(log(price) ~ object_type + private_offer + rooms + square_meters, data=leverage_removed)
summary(model0)
plot(model0)

# compdf = data.frame(ytrue=dfrent$price, yhat=exp(predict(model0, dfrent)))
# ggplot(data=compdf, aes(x=ytrue, y=yhat)) + geom_point(alpha=0.1)

# room x sqm interaction
model1 = lm(log(price) ~ object_type + private_offer + rooms * square_meters, data=leverage_removed)
summary(model1)
plot(model1)


anova(model1, model0)








################### Modelling - Hierarchical ###################


model2 = lmer(log(price) ~ object_type + private_offer + rooms * square_meters + (1 | zip_code), data=leverage_removed)
summary(model2)
# xtable(coef(summary(model2)))


anova(model2, model1)
dotplot(ranef(model2))

ranef(model2)$zip_code

x = ranef(model2, condVar=TRUE)$zip_code
xdf = data.frame(pointest=ranef(model2, condVar=TRUE)$zip_code, err=as.vector(sqrt(attr(x, "postVar"))))
xdf$pointestimate = xdf$X.Intercept.
xdf$zip = rownames(xdf)
xdf$X.Intercept. = NULL
write_parquet(xdf, "data/intermediaries/ranef_by_zipcode.parquet")










######## EXPERIMENT: PREDICTING PPSQM ###########
# dfrent = dfrent %>% filter(ppsqm <= quantile(dfrent$ppsqm, 0.99))
# ggplot(data=dfrent, aes(x=ppsqm)) + geom_histogram()
# 
# mse = function(model, data, ytrue, predict_ppsqm){
#  preds = predict(model, data)
#  if (predict_ppsqm == TRUE){
#    preds = preds * data$square_meters
#  }
#  return(mean((preds - ytrue)^2))
# }
# 
# exp_model0 = lm(ppsqm ~ object_type + private_offer + rooms + square_meters, data=dfrent)
# print(mse(exp_model0, dfrent, dfrent$ppsqm, predict_ppsqm=TRUE))
# 
# exp_model1 = lm(price ~ object_type + private_offer + rooms + square_meters, data=dfrent)
# print(mse(exp_model1, dfrent, dfrent$price, predict_ppsqm=FALSE))
############## END OF EXPERIMENT ################
