package com.pivotseoul.recommend.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;

/** 자치구 추천 요청. 원하는 집 조건 + 월 소득(만원). */
public class RecommendRequest {

    @Pattern(regexp = "youth|family|senior")
    private String lifeStage;

    @Pattern(regexp = "apartment|officetel|house|villa")
    private String houseType;

    @DecimalMin(value = "5", inclusive = false)
    @DecimalMax("300")
    private double areaM2;

    @Min(0)
    @Max(60)
    private int buildingAge;

    @Min(0)
    @Max(80)
    private int floor;

    @Positive
    private double monthlyIncome;

    public String getLifeStage() { return lifeStage; }
    public void setLifeStage(String lifeStage) { this.lifeStage = lifeStage; }

    public String getHouseType() { return houseType; }
    public void setHouseType(String houseType) { this.houseType = houseType; }

    public double getAreaM2() { return areaM2; }
    public void setAreaM2(double areaM2) { this.areaM2 = areaM2; }

    public int getBuildingAge() { return buildingAge; }
    public void setBuildingAge(int buildingAge) { this.buildingAge = buildingAge; }

    public int getFloor() { return floor; }
    public void setFloor(int floor) { this.floor = floor; }

    public double getMonthlyIncome() { return monthlyIncome; }
    public void setMonthlyIncome(double monthlyIncome) { this.monthlyIncome = monthlyIncome; }
}
