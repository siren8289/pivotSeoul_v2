package com.pivotseoul.diagnosis.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

/**
 * 진단 기록 1건 = diagnosis 테이블의 한 줄.
 * 사용자 입력값과 AI 결과를 함께 저장해서, 나중에 결과 화면을 다시 볼 수 있게 한다.
 * 프론트에는 이 객체를 그대로 JSON으로 보내 준다.
 */
@Entity
@Table(name = "diagnosis")
public class Diagnosis {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ---- 사용자 입력 ----
    private String lifeStage;
    private String district;
    private String houseType;
    private double areaM2;
    private int buildingAge;
    private int floor;
    private double monthlyIncome;
    private double deposit;
    private double monthlyRent;

    // ---- 규칙 계산 결과 (RIR) ----
    private double monthlyCost;      // 월 환산 주거비
    private Double rirPercent;       // 소득 대비 주거비 비율(%)
    private String status;           // stable / warning / danger
    private boolean redZone;         // 위험(Red Zone)이면 true

    // ---- ML·DL 결과 (예상 시세) ----
    private double mlPrice;          // ML(랜덤포레스트) 예측
    private double dlPrice;          // DL(신경망) 예측
    private double marketPrice;      // 두 모델의 평균
    private double priceGapPercent;  // 내 주거비가 시세보다 몇 % 비싼지
    private Double districtMedianCost;
    private Integer auditCount;          // 최근 회계감사 단지수 (관리 투명도)

    // ---- LLM 결과 ----
    @Column(length = 2000)
    private String explanation;
    private String explanationSource; // gemini 또는 basic

    private LocalDateTime createdAt = LocalDateTime.now();

    // JPA가 사용하는 기본 생성자
    public Diagnosis() {
    }

    public Long getId() { return id; }

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

    public double getMonthlyCost() { return monthlyCost; }
    public void setMonthlyCost(double monthlyCost) { this.monthlyCost = monthlyCost; }

    public Double getRirPercent() { return rirPercent; }
    public void setRirPercent(Double rirPercent) { this.rirPercent = rirPercent; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public boolean isRedZone() { return redZone; }
    public void setRedZone(boolean redZone) { this.redZone = redZone; }

    public double getMlPrice() { return mlPrice; }
    public void setMlPrice(double mlPrice) { this.mlPrice = mlPrice; }

    public double getDlPrice() { return dlPrice; }
    public void setDlPrice(double dlPrice) { this.dlPrice = dlPrice; }

    public double getMarketPrice() { return marketPrice; }
    public void setMarketPrice(double marketPrice) { this.marketPrice = marketPrice; }

    public double getPriceGapPercent() { return priceGapPercent; }
    public void setPriceGapPercent(double priceGapPercent) { this.priceGapPercent = priceGapPercent; }

    public Double getDistrictMedianCost() { return districtMedianCost; }
    public void setDistrictMedianCost(Double districtMedianCost) { this.districtMedianCost = districtMedianCost; }

    public Integer getAuditCount() { return auditCount; }
    public void setAuditCount(Integer auditCount) { this.auditCount = auditCount; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public String getExplanationSource() { return explanationSource; }
    public void setExplanationSource(String explanationSource) { this.explanationSource = explanationSource; }

    public LocalDateTime getCreatedAt() { return createdAt; }
}
