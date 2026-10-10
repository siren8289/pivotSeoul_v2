package com.pivotseoul.diagnosis.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;

/**
 * 진단 요청 (프론트 → Spring). 금액 단위는 모두 '만원'.
 * 필드 위의 @ 표시는 입력값 검사 규칙이다. 규칙에 어긋나면 400 오류가 난다.
 */
public class DiagnosisRequest {

    // youth(청년) / family(신혼·육아) / senior(중장년·노년)
    @Pattern(regexp = "youth|family|senior")
    private String lifeStage;

    // 자치구 이름. 예) 마포구
    @NotBlank
    private String district;

    // apartment(아파트) / officetel(오피스텔) / house(단독·다가구) / villa(연립·다세대)
    @Pattern(regexp = "apartment|officetel|house|villa")
    private String houseType;

    // 전용면적(㎡)
    @DecimalMin(value = "5", inclusive = false)
    @DecimalMax("300")
    private double areaM2;

    // 건물 나이(년)
    @Min(0)
    @Max(60)
    private int buildingAge;

    @Min(0)
    @Max(80)
    private int floor;

    @Positive
    private double monthlyIncome;   // 월 소득

    @PositiveOrZero
    private double deposit;         // 보증금

    @PositiveOrZero
    private double monthlyRent;     // 월세

    public String getLifeStage() { return lifeStage; }
    public void setLifeStage(String lifeStage) { this.lifeStage = lifeStage; }

    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }

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

    public double getDeposit() { return deposit; }
    public void setDeposit(double deposit) { this.deposit = deposit; }

    public double getMonthlyRent() { return monthlyRent; }
    public void setMonthlyRent(double monthlyRent) { this.monthlyRent = monthlyRent; }
}
