

################### Modelling - Hierarchical ###################
leverage_removed$std_log_price = scale(log(leverage_removed$price))

# model2 = lmer(log(price) ~ object_type + private_offer + rooms * square_meters + (1 | zip_code), data=leverage_removed)
model2 = lmer(std_log_price ~ object_type + private_offer + rooms * square_meters + (1 | zip_code), data=leverage_removed)
summary(model2)
# xtable(coef(summary(model2)))


anova(model2, model1)
dotplot(ranef(model2))

if(OUTPUT_TABLES){
  print(xtable(summary(model2)$coefficients), file="documents/scripts_output/rentals_model2_summary.tex")
}

## Export Section
ranef(model2)$zip_code
x = ranef(model2, condVar=TRUE)$zip_code
xdf = data.frame(pointest=ranef(model2, condVar=TRUE)$zip_code, err=as.vector(sqrt(attr(x, "postVar"))))
xdf$pointestimate = xdf$X.Intercept.
xdf$zip = rownames(xdf)
xdf$X.Intercept. = NULL
write_parquet(xdf, "data/intermediaries/ranef_by_zipcode_rentals.parquet")
#######################

################## Model Assessment ###################

assess_df = data.frame(preds = fitted(model2), ytrue=log(leverage_removed$price))
assess_df$residuals = assess_df$preds - assess_df$ytrue
ggplot(data=assess_df, aes(x=preds, y=residuals)) + geom_point(alpha=0.2) + theme_bw()
ggplot(data=assess_df, aes(sample=residuals)) + geom_qq() + geom_qq_line() + theme_bw()


################# Random Slopes ##################
# Convergence error
# model2 = lmer(std_log_price ~ object_type + private_offer + rooms + (square_meters | zip_code), data=leverage_removed)


################ Checking Missingness ################
missing_mod = glm((dfrent$rooms == "Missing") ~ object_type + private_offer + square_meters, family=binomial, data=dfrent)
summary(missing_mod)




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

