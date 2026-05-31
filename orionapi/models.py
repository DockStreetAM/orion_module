"""Auto-generated TypedDicts for Eclipse v2 response/request DTOs.

Generated from API Docs/EclipseV2Swagger.json. Static typing only — the
EclipseV2 methods still return plain dicts/lists at runtime.
"""

from __future__ import annotations

from typing import Any, TypedDict


class AccountOptimizationBatchRequested(TypedDict, total=False):
    batchId: str
    optimizationType: str
    accountIds: list[str]
    activeThreshold: int
    overrides: BatchOptimizationOverrides


class BatchOptimizationOverrides(TypedDict, total=False):
    taxLambda: float
    factorLambda: float
    stockSpecificLambda: float
    maxCapitalGainsBudget: float
    maxNumberOfAssets: int
    raiseCashTargetAmount: float
    harvestLossThresholdPercent: float
    ignoreMaxGains: bool


class ConfigurationDto(TypedDict, total=False):
    metadata: WebComponentStorageMetadataDto
    roleId: int
    firmId: int
    tradeToolSettings: ConfigurationTradeTool
    preferenceSettings: list[ConfigurationPreferenceDto]


class ConfigurationPreferenceDto(TypedDict, total=False):
    id: int
    categoryType: str
    name: str
    enabled: bool


class ConfigurationTradeTool(TypedDict, total=False):
    overridesEnabled: bool
    tradeQueueLogic: int
    defaultProductClassification1: int
    defaultProductClassification2: int


class CustodianExecutionSettingDto(TypedDict, total=False):
    id: int
    name: str
    routing: str
    masterAccountNumber: str
    securityTypeId: int
    isOmnibusAllocation: bool


class EclipseFirmDto(TypedDict, total=False):
    alClientId: int
    orionConnectFirmName: str
    eclipseFirmId: int
    eclipseFirmName: str


class ExecutingDestinationDto(TypedDict, total=False):
    id: int
    name: str
    securityTypeId: int


class ExecutingDestinationWithTypeDto(TypedDict, total=False):
    id: int
    name: str
    executionDestinationTypeId: int


class AccountPreferencesRequestDto(TypedDict, total=False):
    preferenceNames: list[str]
    accountIds: list[int]


class AccountPreferencesResponseDto(TypedDict, total=False):
    accountId: int
    preferenceName: str
    preferenceValue: str
    indicatorValue: str


class SecuritySettingPreferenceEquivalent(TypedDict, total=False):
    relatedTypeId: str
    relatedType: str
    targetedSecurityId: int
    targetedSecurityName: str
    targetedSecuritySymbol: str
    equivalentSecurityId: int
    equivalentSecurityName: str
    equivalentSecuritySymbol: str
    sellPriorityId: int
    sellPriorityName: str
    buyPriorityId: int
    buyPriorityName: str


class TradeDto(TypedDict, total=False):
    id: int
    registrationName: str
    portfolioId: int
    securityId: int
    accountId: int
    tradeInstanceId: int
    custodian: str
    custodianId: int
    tradeAmount: float
    action: int
    status: str
    createdDate: str
    isEnabled: bool
    orderQty: float
    orderPercent: float
    price: float
    warningMessage: str
    createdBy: int
    editedBy: int
    editedDate: str
    isDeleted: bool
    orderTypeId: int
    instanceNotes: str
    notes: str
    originalOrderQty: float
    isTLH: bool
    orderStatus: int
    accountNumber: str
    ticker: str
    productName: str
    accountType: str
    astroTradeId: int


class TradesCountDto(TypedDict, total=False):
    openOrdersCount: int
    noOfTradeBlocks: int
    unallocatedBlocks: int
    pendingOrdersCount: int
    noOfClosedTrades: int
    tradesFileCount: int
    noOfFixedTrades: int
    mfBatchesAndAwaitingOrderCount: int


class UpdateTradeBlocksRequestDto(TypedDict, total=False):
    blockIds: list[int]
    executingBrokerId: int
    executingDestinationId: int
    allocationDestinationId: int
    orderTypeId: int
    orderStatusId: int
    limitPrice: float
    stopPrice: float
    averagePrice: float
    custodianAlgoTagId: int
    algoInstruction: str
    durationId: int
    qualifierId: int
    isDiscretionary: bool
    isAutoAllocate: bool


class TrimTradeOrderDetailDto(TypedDict, total=False):
    tradeId: int
    portfolioId: int
    portfolioName: str
    accountId: str
    ticker: str
    existingPrice: float
    securityType: str
    existingQuantity: float
    existingAmount: float
    action: str
    messages: str


class UpdateMassTradeOrderRequestDto(TypedDict, total=False):
    orderIds: list[int]
    durationId: int
    qualifierId: int
    orderConditionTypeName: str
    notes: str
    holdUntil: str
    holdUntilAction: str


class WebComponentStorageMetadataDto(TypedDict, total=False):
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str


class CustomImportInstanceStageDataRow(TypedDict, total=False):
    rowId: int
    rowNumber: int
    statusId: int
    message: str
    namedColumns: dict[str, Any]


class ImportInstanceFlattenedStagedData(TypedDict, total=False):
    instanceId: int
    instanceName: str
    overrideInstanceId: int
    instanceStatusName: str
    templateType: str
    templateId: int
    createdBy: str
    createdOn: str
    editedBy: str
    editedOn: str
    rows: list[CustomImportInstanceStageDataRow]


class InvestorPreferencesSettings(TypedDict, total=False):
    benchmarkID: str
    riskModel: int
    minPortCash: float
    maxPortCash: float
    maxCapitalGains: float
    shortTermGainRate: float
    longTermGainRate: float
    ticketCharge: float
    minTrackErr: float
    maxTrackErr: float
    maxNoSec: int
    minSecExp: float
    maxSecExp: float
    maxTurnover: float
    minThreshold: float
    maxTrades: int
    minTradeType: str
    minTradeSize: float
    industryStyle: str
    sectorStyle: str
    withHoldCashForTransactionCosts: bool
    withHoldCashForTaxes: bool
    strategyName: str
    istUser: str
    isPreferenceExist: bool
    buyStyle: str
    excludeHoldFromBuyList: bool
    isAutoExposure: bool
    unsetCompositeAssets: bool
    saveAttributeData: bool
    enableNLTC: bool
    astroError: str
    restrictSTGains: bool


class RiskModelExceptionsRequest(TypedDict, total=False):
    productIds: list[int]
    riskModel: str


class SaveInvestorPreferenceRequestDto(TypedDict, total=False):
    astroTemplate: str
    astroWithholdCashForTaxes: str
    enableNLTC: bool
    excludeHoldFromBuyList: bool
    accountMaxGainAmount: float
    maximumNoSecurities: int
    maximumAccountCash: float
    minimumAccountCash: float
    maximumTrackingError: float
    maximumTurnover: float
    minimumSecurityExposure: float
    maximumSecurityExposure: float
    minimumThreshold: float
    minimumTrackingError: float
    targetStrategy: str
    ticketCharge: float
    unsetCompositeAssets: bool
    withHoldCashForTransactionCosts: bool
    astroError: str
    minimumTradeType: str
    minimumTradeSize: float
    maximumTrades: int
    isEdited: bool
    allowShortTermGains: str
    updateCashFields: bool
    exposureModel: str
    shortTermGainRate: float
    longTermGainRate: float


class SaveInvestorPreferencesRequest(TypedDict, total=False):
    isEdited: bool
    editedInvestorPreferences: SaveInvestorPreferenceRequestDto


class SectorIndustrySaveResponse(TypedDict, total=False):
    isError: bool
    message: str
    response: str


class SimpleResponse(TypedDict, total=False):
    hasError: bool
    message: str


class WithdrawCashOptimizationRequest(TypedDict, total=False):
    accountId: int
    withdrawAmount: int
    optType: int
    maxTrackErr: int
    minTrackErr: int
    maxCapitalGains: int
    minTradeSizePCT: int
    maxTrades: int
    includeCash: bool
    onlySellSecurities: bool
    optSource: int


class UserGridView(TypedDict, total=False):
    id: int
    orionExternalId: int
    viewTypeId: int
    gridColumnDefs: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class CommunityModelUnAssignment(TypedDict, total=False):
    modelId: int
    name: str
    portfolioId: int
    accountId: int
    communityModelId: int


class DateAccountSetAside(TypedDict, total=False):
    id: int
    name: str
    accountId: int
    accountNumber: str
    sleeveType: str
    portfolioId: int
    description: str
    startDate: str
    expireDate: str
    cashAmount: float
    createdDate: str
    minCashAmount: float
    systemExpiredOn: str


class ExpiredAccountSetAside(TypedDict, total=False):
    id: int
    name: str
    accountId: int
    accountNumber: str
    sleeveType: str
    portfolioId: int
    description: str
    cashAmount: float
    setAsideCashExpirationType: str
    expireTransactionType: str
    createdDate: str
    systemExpiredOn: str
    isDepleteOverTime: bool
    startDate: str


class FixMessage(TypedDict, total=False):
    id: int
    blockOrderId: int
    msgType: str
    createdDate: str
    logText: str
    fixDetails: str


class LevelData(TypedDict, total=False):
    assetId: int
    assetName: str
    currentAmount: float
    currentInPercentage: float
    currentPrice: float
    differenceInPercentage: float
    modelElementId: int
    postTradeAmount: float
    postTradeInPercentage: float
    relatedTypeCode: str
    targetInDollar: float
    targetInPercentage: float
    targetInShares: float
    isModelSecurity: bool


class MacDetail(TypedDict, total=False):
    ticker: str
    weighting: str
    isTaxable: bool
    isTaxDeferred: bool
    isTaxExempted: bool
    rank: int
    editedBy: str
    editedDate: str
    createdBy: str
    createdDate: str
    changeType: str


class MacStatus(TypedDict, total=False):
    status: str
    editedBy: str
    editedDate: str
    createdBy: str
    createdDate: str
    changeType: str


class Team(TypedDict, total=False):
    portfolioId: int
    teamId: int
    teamName: str
    isPrimaryTeam: int
    portfolioAccess: int


class PortfolioFlag(TypedDict, total=False):
    portfolioId: int
    needAnalytics: int
    needAnalyticsToTrade: int
    failedReason: str
    managedValue: float
    modelId: int
    analyticsEditedDate: str


class SimplePortfolioValuesSummary(TypedDict, total=False):
    cashValue: float
    totalCash: float
    cashDifference: float
    costBasis: float
    marketValue: float
    managedValue: float


class TradeModel(TypedDict, total=False):
    id: int
    name: str


class TransactionsForSetAsides(TypedDict, total=False):
    accountNumber: str
    transactionId: int
    transactionExternalId: int
    symbol: str
    tradeDate: str
    amount: float
    type: str
    status: str
    setAsideId: int


class UnexpiredAccountSetAside(TypedDict, total=False):
    id: int
    name: str
    accountId: int
    accountNumber: str
    sleeveType: str
    portfolioId: int
    description: str
    cashAmount: float
    setAsideCashExpirationType: str
    expireTransactionType: str
    createdDate: str
    systemExpiredOn: str
    transactionAmountTolerance: float
    totalTransactionAmount: float
    dollarsDifferenceIndividually: float
    percentDifferenceIndividually: float
    percentDifferenceAggregated: float
    dollarsDifferenceAggregated: float
    isDepleteOverTime: bool
    startDate: str


class Account(TypedDict, total=False):
    id: int
    orionConnectExternalId: int
    orionConnectFirmId: int
    accountId: str
    accountNumber: str
    name: str
    portfolioId: int
    householdId: int
    restrictedPlanId: int
    ytdRealizedStgl: float
    ytdRealizedLtgl: float
    washSaleGroup: str
    sweepSymbol: str
    custodianId: int
    custodialAccountNumber: str
    sleeveType: str
    createdDate: str
    householdName: str
    accountTypeId: int
    createdBy: int
    editedDate: str
    editedBy: int
    isDeleted: bool
    advisorId: int
    sweepSecurityId: int
    systematicAmount: float
    systematicDate: str
    sma: bool
    smaTradeable: str
    billingAccount: int
    sleeveTarget: float
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    sleeveToleranceLower: float
    sleeveToleranceUpper: float
    modelId: int
    isDisabled: bool
    disabledReason: str
    hashedSsn: str
    orionEclipseFirmId: int
    substitutedModelId: int
    deletedReason: str
    isCustodialRestriction: bool
    isDoNotBuySell: bool
    tradingInstr: str
    maxTrackingError: float
    minTrackingError: float
    astroEnabled: bool
    monthlySystematicWithdrawal: float
    nextMonthlySystematicWithdrawalDate: str
    quarterlySystematicWithdrawal: float
    nextQuarterlySystematicWithdrawalDate: str
    semiAnnualSystematicWithdrawal: float
    nextSemiAnnualSystematicWithdrawalDate: str
    annualSystematicWithdrawal: float
    nextAnnualSystematicWithdrawalDate: str
    systematicPurchase: float
    nextSystematicPurchaseDate: str
    registrationId: int
    type: AccountType
    custodian: Custodian
    restrictedPlan: RestrictedPlan
    portfolio: Portfolio
    model: Model
    accountAccessibleToUsers: list[AccountAccessibleToUser]
    setAsideCashes: list[AccountSetAsideCash]
    accountSmaAllocations: list[AccountSmaAllocation]
    tags: str
    importErrorPositions: list[ImportErrorPosition]
    importErrorTaxLots: list[ImportErrorTaxLot]
    outSourcedStatus: str
    accountExtension: AccountExtension
    companionEclipseFirmId: int


class AccountAccessibleToUser(TypedDict, total=False):
    userId: int
    accountId: int


class AccountExcludedCashInfo(TypedDict, total=False):
    excludedCashTarget: float
    excludedCashActual: float
    totalValue: float


class AccountExtension(TypedDict, total=False):
    id: int
    accountId: int
    portfolioId: int
    eclipseCreatedDate: str
    howPortfolioAssigned: int
    tradingNotes: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isExcluded: bool
    rebalanceOptionId: int
    rebalanceDay: int


class AccountIdBasicInfo(TypedDict, total=False):
    id: int
    orionConnectExternalId: int
    orionConnectFirmId: int


class AccountSmaAllocation(TypedDict, total=False):
    id: int
    accountId: int
    account: Account
    modelId: int
    modelDetailId: int
    modelDetail: ModelDetail
    weightPercent: float
    subModelId: int
    levelId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class AccountTags(TypedDict, total=False):
    accountIds: list[int]
    addTags: list[str]
    removeTags: list[str]


class AccountTradeBlocked(TypedDict, total=False):
    id: int
    isDoNotBuySell: bool
    isCustodialRestriction: bool


class AccountType(TypedDict, total=False):
    id: int
    name: str
    taxableType: int
    code: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class ExternalAccountInfo(TypedDict, total=False):
    orionConnectExternalId: int
    orionConnectFirmId: int
    hasPendingOrders: bool


class RestrictedPlan(TypedDict, total=False):
    id: int
    restrictedPlanName: str
    useInTradeFile: int
    externalPlanId: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    securities: list[RestrictedPlanSecurities]


class Custodian(TypedDict, total=False):
    id: int
    orionFirmId: int
    externalId: int
    name: str
    code: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    tradeExecutionTypeId: int
    masterAccountNumber: str
    orionEclipseFirmId: int
    routing: str
    fixVersion: str
    fixBankId: str
    tdaUserId: str
    tdaNamespace: str
    houseAccountId: str
    allowFractionalEquityOrder: bool
    fractionalEquityPrecision: int
    allocationMethod: int
    isAllowTradeAway: bool
    commissions: float
    fees: float
    isDisableFixBlockRounding: bool
    executingBrokerId: int
    allocationDestinationId: int
    allocationInstructionId: int
    customAllocationMessage: str
    mpid: str
    setAutomaticAlgo: bool
    tradeExecutions: list[CustodianTradeExecutionTypeForSecurity]
    custodianAlgoTags: list[CustodianAlgoTagInfo]
    allowOnlyCreateFractionalShareLiquidationTrades: bool
    isSendOrderCondition: bool
    isSendBrokerAllocationMessage: bool
    custodianExecutionSettingsForSecurityType: list[CustodianExecutionSettingsForSecurityType]


class CustodianAlgoTagInfo(TypedDict, total=False):
    id: int
    custodianId: int
    tag: str
    algoName: str
    algoInstruction: str
    rangeFromValue: int
    rangeToValue: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    customFixTags: list[CustomFixTagDefinition]


class CustodianExecutionSettingsForSecurityType(TypedDict, total=False):
    id: int
    custodianId: int
    securityTypeId: int
    tradeExecutionTypeId: int
    isAllowTradingAway: int
    executionDestinationId: int
    allocationDestinationId: int
    executionDestinationTypeId: int
    allocationTradeExecutionTypeId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class CustodianTradeExecutionTypeForSecurity(TypedDict, total=False):
    custodianId: int
    securityTypeId: int
    tradeExecutionTypeId: int
    allocationTradeExecutionTypeId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class CustomFixTagDefinition(TypedDict, total=False):
    id: int
    customTagType: int
    custodianId: int
    custodianAlgoTagInfoId: int
    broker: str
    displayName: str
    algoType: str
    fixTag: int
    dataType: int
    minimumValue: float
    maximumValue: float
    decimalPrecision: int
    required: bool
    enumPairs: list[EnumPair]
    defaultValue: str
    createdBy: int
    createdDate: str
    editedBy: int
    editedDate: str
    displayOrder: int
    custodianAlgoTagInfo: CustodianAlgoTagInfo


class EnumPair(TypedDict, total=False):
    label: str
    value: str
    displayOrder: int


class ExecutionDestinationType(TypedDict, total=False):
    id: int
    name: str
    createdDate: str


class Privilege(TypedDict, total=False):
    id: int
    code: str
    name: str
    type: int
    userLevel: int
    categoryId: int
    preferenceRequiredForDisplay: int
    preferenceId: int
    description: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    displayOrder: int
    rolePrivileges: list[RolePrivilege]


class Role(TypedDict, total=False):
    id: int
    name: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    roleTypeId: int
    startDate: str
    expireDate: str
    status: bool
    rollType: RoleType
    users: list[User]
    rolePrivileges: list[RolePrivilege]


class RolePrivilege(TypedDict, total=False):
    id: int
    roleId: int
    privilegeId: int
    canAdd: bool
    canUpdate: bool
    canDelete: bool
    canRead: bool
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    role: Role
    privilege: Privilege


class RoleType(TypedDict, total=False):
    id: int
    type: str
    bitValue: int
    roles: list[Role]


class Administration_Team(TypedDict, total=False):
    id: int
    name: str
    orionFirmId: int
    externalId: int
    portfolioAccess: int
    modelAccess: int
    securitySetAccess: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    status: int
    canEditAllModels: bool
    userTeams: list[UserTeam]


class User(TypedDict, total=False):
    id: int
    orionConnectExternalId: int
    firstName: str
    lastName: str
    roleId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    email: str
    status: int
    tags: str
    theme: str
    startDate: str
    expireDate: str
    userLoginId: str
    notificationEmail: str
    role: Role
    userTeams: list[UserTeam]
    notificationSubscriptions: list[NotificationSubscription]


class UserTeam(TypedDict, total=False):
    userId: int
    teamId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isPrimary: bool
    user: User
    team: Administration_Team


class AnalyticsWorkingBatch(TypedDict, total=False):
    batchIdentifier: str
    portfolioId: int
    createdDate: str
    tradeInstanceId: int
    portfolioAnalyticsFlag: PortfolioAnalyticsFlag


class BatchJob(TypedDict, total=False):
    id: int
    type: str
    description: str
    startedDate: str
    completedDate: str
    status: str
    errorCount: int
    successCount: int
    totalCount: int
    percentComplete: int
    createdBy: str
    parameters: str
    correlationId: str
    batchJobDetails: list[BatchJobDetail]


class BatchJobDetail(TypedDict, total=False):
    id: int
    batchJobId: int
    batchJob: BatchJob
    record: str
    recordId: str
    status: str
    message: str


class CustomImportBlob(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    fileBytes: str
    filename: str
    extension: str
    template: CustomImportTemplate


class CustomImportInstance(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    templateId: int
    template: CustomImportTemplate
    importName: str
    instanceStateId: int
    instanceState: CustomImportInstanceState
    overrideInstanceId: int
    overrideInstance: CustomImportInstance
    message: str
    instanceRows: list[CustomImportInstanceRow]


class CustomImportInstanceRow(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    rowNumber: int
    instanceId: int
    instance: CustomImportInstance
    instanceRowStateId: int
    instanceRowState: CustomImportInstanceRowState
    message: str
    operationCode: str
    columns: list[CustomImportInstanceRowColumn]


class CustomImportInstanceRowColumn(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    templateColumnId: int
    templateColumn: CustomImportTemplateColumn
    instanceRowId: int
    row: CustomImportInstanceRow
    oldValue: str
    newValue: str


class CustomImportInstanceRowState(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    stateValue: str
    stateDescription: str
    instanceRows: list[CustomImportInstanceRow]


class CustomImportInstanceState(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    stateValue: str
    stateDescription: str
    instances: list[CustomImportInstance]


class CustomImportTemplate(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    templateName: str
    blobId: int
    blob: CustomImportBlob
    isOverridable: bool
    instances: list[CustomImportInstance]
    columns: list[CustomImportTemplateColumn]
    userPreferences: list[CustomImportUserPreference]


class CustomImportTemplateColumn(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    id: int
    templateId: int
    template: CustomImportTemplate
    columnName: str
    displayName: str
    dataType: str
    displayOrder: int
    isHeader: bool
    isRequired: bool
    hint: str
    validValues: str


class CustomImportUserPreference(TypedDict, total=False):
    createdBy: int
    createdByUser: User
    createdDate: str
    editedBy: int
    editedByUser: User
    editedDate: str
    userId: int
    templateId: int
    template: CustomImportTemplate
    isFavorite: bool


class ImportErrorPosition(TypedDict, total=False):
    id: int
    metaTableId: int
    errorMessage: str
    orionFirmId: int
    externalId: int
    symbol: str
    price: float
    accountNumber: str
    accountId: str
    account: Account
    marketValue: float
    quantity: float
    positionYtdRealizedShortTermGainLoss: float
    positionYtdRealizedLongTermGainLoss: float


class ImportErrorTaxLot(TypedDict, total=False):
    id: int
    metaTableId: int
    errorMessage: str
    orionFirmId: int
    externalId: int
    accountId: str
    account: Account
    symbol: str
    accountNumber: str
    dateAcquired: str
    quantity: float
    costAmount: float
    costPerShare: float
    price: float
    marketValue: float
    isLongTerm: bool


class Model(TypedDict, total=False):
    id: int
    name: str
    nameSpace: str
    statusId: int
    description: str
    dynamicModel: bool
    scope: str
    tags: str
    managementStyleId: int
    modelManagementStyle: ModelManagementStyle
    ownerUserId: int
    approvedBy: int
    isSubModel: bool
    isCommunityModel: bool
    communityModelId: int
    isSubstitutedForPortfolio: bool
    isSubstitutedForSleeve: bool
    substituteOfModelId: int
    isDeleted: bool
    changeSource: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    astroEnabled: bool
    astroTemplateId: str
    astroUsage: int
    syncToAstro: bool
    isSMA: bool
    sleeveSuffix: str
    optionLevel: str
    primeBrokerage: str
    marginAgreement: str
    modelTypeId: int
    modelType: ModelType
    lastRebalanced: str
    dateRebalanceRequested: str
    details: list[ModelDetail]
    modelAccesibleToUsers: list[ModelAccessibleToUser]


class ModelAccessibleToUser(TypedDict, total=False):
    userId: int
    user: User
    modelId: int
    model: Model
    canEdit: bool


class ModelAnalyzer(TypedDict, total=False):
    portfolioId: int
    accountId: int
    accountTaxType: str
    custodian: str
    isSmaNode: bool
    isMACSecurity: bool
    parentModelDetailId: int
    symbol: str
    securityType: str
    securityName: str
    securityTypeId: int
    securityId: int
    cusip: str
    productCategoryName: str
    productClassName: str
    productSubClassName: str
    targetSecurityName: str
    targetSecurityId: int
    targetSecuritySymbol: str
    targetSecurityType: str
    securityEffectiveTargetPercentage: float
    securityEffectiveTargetAmount: float
    securityEffectiveUpperTolerance: float
    securityEffectiveLowerTolerance: float
    securityEffectiveUpperAmount: float
    securityEffectiveLowerAmount: float
    securitySetName: str
    securitySetId: int
    securitySetEffectiveTargetPercentage: float
    securitySetEffectiveTargetAmount: float
    securitySetEffectiveUpperTolerance: float
    securitySetEffectiveLowerTolerance: float
    securitySetEffectiveUpperAmount: float
    securitySetEffectiveLowerAmount: float
    subClassName: str
    subClassEffectiveTargetPercentage: float
    subClassEffectiveTargetAmount: float
    subClassEffectiveUpperTolerance: float
    subClassEffectiveLowerTolerance: float
    subClassEffectiveUpperAmount: float
    subClassEffectiveLowerAmount: float
    className: str
    classEffectiveTargetPercentage: float
    classEffectiveTargetAmount: float
    classEffectiveUpperTolerance: float
    classEffectiveLowerTolerance: float
    classEffectiveUpperAmount: float
    classEffectiveLowerAmount: float
    categoryName: str
    categoryEffectiveTargetPercentage: float
    categoryEffectiveTargetAmount: float
    categoryEffectiveUpperTolerance: float
    categoryEffectiveLowerTolerance: float
    categoryEffectiveUpperAmount: float
    categoryEffectiveLowerAmount: float
    modelName: str
    aggregatedPostAmount: float
    aggregatedPostPercentage: float
    aggregatedCurrentAmount: float
    aggregatedCurrentPercentage: float
    assetMACWeightingName: str
    macWeightPercentage: float
    equivalentLevel: str
    orionConnectExternalId: int
    sleeveStrategyName: str
    suffix: str
    orionAccountID: str
    orionAccountNumber: str
    orionAccountName: str
    sleeveModelName: str
    sleeveModelID: int
    excludedSleeve: bool
    doNotTradeAccount: bool
    portfolioManagedValue: float
    sleeveUpperTolerancePercentage: float
    sleeveLowerTolerancePercentage: float
    sleeveContributionPercentage: float
    sleeveDistributionPercentage: float
    journalAmount: float
    journalPercentage: float
    sleeveTargetPercentage: float
    excludedValue: float
    sleeveStrategyAggregateLowerTolerance: float
    sleeveStrategyAggregateUpperTolerance: float
    securitySetModelIsSubstituted: bool
    subClassModelIsSubstituted: bool
    classModelIsSubstituted: bool
    categoryModelIsSubstituted: bool


class ModelDetail(TypedDict, total=False):
    id: int
    modelId: int
    modelElementId: int
    leftValue: int
    rightValue: int
    rank: int
    level: str
    isSubstituted: bool
    substituteOf: int
    targetPercent: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    toleranceType: int
    toleranceTypeValue: float
    lowerModelToleranceAmount: float
    upperModelToleranceAmount: float
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    model: Model
    modelElement: ModelElement


class ModelElement(TypedDict, total=False):
    id: int
    name: str
    relatedType: str
    relatedTypeId: int
    isFavorite: bool
    namespace: str
    forCopy: bool
    validateTickerSet: bool
    rebalancePriority: int
    tags: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    securitySet: SecuritySet


class ModelManagementStyle(TypedDict, total=False):
    id: int
    name: str
    models: list[Model]


class ModelType(TypedDict, total=False):
    id: int
    name: str
    models: list[Model]


class AllocationNotification(TypedDict, total=False):
    blockId: int
    allocationStatusId: int


class BlockNotification(TypedDict, total=False):
    blockId: int


class MenuNotification(TypedDict, total=False):
    typeId: str
    total: int
    increment: int
    code: str
    instanceId: int


class Notification(TypedDict, total=False):
    id: int
    subject: str
    body: str
    notificationCategoryTypeId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    severityType: str
    subCode: str
    instanceId: int


class NotificationCategory(TypedDict, total=False):
    id: int
    code: str
    enabled: bool
    sendEmail: bool
    isDeleted: bool
    createdOn: str
    editedOn: str
    createdBy: int
    editedBy: int
    name: str


class NotificationCategoryType(TypedDict, total=False):
    id: int
    name: str
    code: str
    userLevel: int
    description: str
    subject: str
    iconUrl: str
    deliveryMode: int
    notificationCategoryId: int
    isDeleted: bool
    notificationSubscriptions: list[NotificationSubscription]


class NotificationCategoryTypeTable(TypedDict, total=False):
    id: int
    name: str
    code: str
    iconUrl: str


class NotificationMessage(TypedDict, total=False):
    typeId: int
    code: str
    menuNotification: MenuNotification
    progressNotification: ProgressNotification
    userNotification: UserNotification
    blockNotification: BlockNotification
    orderNotification: OrderNotification
    processTradeProgressNotification: ProcessTradeProgressNotification
    allocationNotification: AllocationNotification
    tradeToolProgressNotification: TradeToolNotification
    portfolioFlag: list[PortfolioAnalyticsFlag]
    notificationCount: int
    totalNotificationsCount: int
    severityType: str
    analyticCount: int
    firmId: int
    trigger: str
    lastImportedDate: str


class NotificationSubscription(TypedDict, total=False):
    userId: int
    user: User
    notificationCategoryTypeId: int
    notificationCategoryType: NotificationCategoryType
    enabled: bool
    sendEmail: bool
    createdBy: int
    createdDate: str
    editedBy: int
    editedDate: str
    isDeleted: bool


class OrderNotification(TypedDict, total=False):
    processedIds: list[int]
    processedCount: int
    unprocessedIds: list[int]
    unprocessedCount: int
    processedBlockIds: list[int]


class ProcessTradeProgressNotification(TypedDict, total=False):
    type: str
    description: str
    startedDate: str
    completedDate: str
    receivedTime: str
    status: str
    errorCount: int
    successCount: int
    totalCount: int
    percentComplete: int
    createdBy: str
    parameters: str
    message: str
    correlationId: str


class ProgressNotification(TypedDict, total=False):
    message: str
    progress: int
    status: str
    processId: str
    type: str
    receivedOn: str


class TradeToolNotification(TypedDict, total=False):
    message: str
    type: str
    process: str
    progress: int
    status: str
    processId: int
    tradeToolName: str
    initiatedUserId: int
    tradeInstanceId: int
    holdProgressBar: bool


class TradingNotificationRequest(TypedDict, total=False):
    userId: int
    firmId: int
    subject: str
    body: str
    isError: bool


class UserNotification(TypedDict, total=False):
    id: int
    subject: str
    body: str
    readStatus: int
    notificationCategory: NotificationCategory
    notificationCategoryType: NotificationCategoryTypeTable
    isDeleted: bool
    createdOn: str
    createdBy: str
    editedOn: str
    editedBy: str
    subCode: str
    errorCount: int
    instanceId: int


class Advisor(TypedDict, total=False):
    id: int
    orionFirmId: int
    externalId: int
    advisorNumber: str
    name: str
    brokerDealer: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    orionEclipseFirmId: int


class Portfolio(TypedDict, total=False):
    id: int
    name: str
    description: str
    modelId: int
    model: Model
    substitutedModelId: int
    substitutedModel: Model
    tags: str
    isDisabled: bool
    disabledReason: str
    isSleevePortfolio: bool
    sleeveContributionMethod: str
    sleeveDistributionMethod: str
    sleeveStrategyName: str
    registrationId: int
    doNotTrade: bool
    tradingInstruction: str
    sellEmphasisOn: int
    buyEmphasisOn: int
    householdId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    orionConnectFirmId: int
    portfolioGroupId: int
    portfolioGroupName: str
    trades: list[Trade]
    teamAccess: list[TeamPortfolioAccess]
    portfolioAccessibleToUsers: list[PortfolioAccessibleToUser]
    accounts: list[Account]
    portfolioAnalyticsFlags: PortfolioAnalyticsFlag
    portfolioExtension: PortfolioExtension


class PortfolioAccessibleToUser(TypedDict, total=False):
    userId: int
    portfolioId: int


class PortfolioAnalyticsFlag(TypedDict, total=False):
    portfolioId: int
    needAnalytics: int
    analyticsType: str
    failedReason: str
    createdDate: str
    editedDate: str
    needAnalyticsToTrade: bool
    analyticsWorkingBatches: list[AnalyticsWorkingBatch]


class PortfolioExtension(TypedDict, total=False):
    id: int
    portfolioId: int
    rebalanceOptionId: int
    rebalanceOption: RebalanceOption
    rebalanceDay: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class PortfolioInfoByExternalAccountId(TypedDict, total=False):
    portfolioId: int
    portfolioName: str
    accountId: int


class PortfolioModelAssignment(TypedDict, total=False):
    portfolioId: int
    modelId: int


class PortfolioTradeBlocked(TypedDict, total=False):
    id: int
    doNotTrade: bool


class RebalanceOption(TypedDict, total=False):
    id: int
    autoRebalanceTypeId: int
    rebalanceMonth: str


class TeamPortfolioAccess(TypedDict, total=False):
    teamId: int
    team: Administration_Team
    portfolioId: int
    access: bool
    isDeleted: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isPrimary: int
    source: str


class UserGridDefaultView(TypedDict, total=False):
    id: int
    viewId: int
    userId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class UserGridRankedView(TypedDict, total=False):
    id: int
    userId: int
    viewId: int
    viewTypeId: int
    rank: int
    createdBy: int
    createdDate: str
    editedBy: int
    editedDate: str


class SavedView_UserGridView(TypedDict, total=False):
    id: int
    viewName: str
    viewTypeId: int
    isPublic: bool
    gridColumnDefs: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    tradeToolId: int
    defaultViews: list[UserGridDefaultView]


class AssetCategory(TypedDict, total=False):
    id: int
    name: str
    orionEclipseName: str
    color: str
    isImported: bool
    isFixedIncomeTrading: bool
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class AssetClass(TypedDict, total=False):
    id: int
    name: str
    assetCategoryId: int
    orionEclipseName: str
    color: str
    isImported: bool
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class AssetSubClass(TypedDict, total=False):
    id: int
    name: str
    assetClassId: int
    orionEclipseName: str
    color: str
    isImported: bool
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class RestrictedPlanSecurities(TypedDict, total=False):
    id: int
    restrictedPlanId: int
    securityId: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    buyPriority: int
    sellPriority: int


class Security(TypedDict, total=False):
    id: int
    orionFirmId: int
    orionConnectExternalId: int
    symbol: str
    name: str
    orionEclipseName: str
    assetCategoryId: int
    assetClassId: int
    assetSubClassId: int
    securityType: int
    status: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isCustodialCash: bool
    orionEclipseFirmId: int
    isSystemGenerated: bool
    cusip: str
    maintainInEclipse: bool
    isMultiAssetClass: int
    parentSecurityId: int
    optionType: str
    expirationDate: str
    price: SecurityPrice
    isTradableMoneyMarket: bool
    assetClass: AssetClass
    assetCategory: AssetCategory
    assetSubClass: AssetSubClass


class SecurityPrice(TypedDict, total=False):
    id: int
    securityId: int
    price: float
    priceType: str
    priceDateTime: str
    isDeleted: int
    createddate: str
    createdBy: int
    editeddate: str
    updatedBy: str
    editedBy: int
    custodianPriceSourceId: int
    security: Security


class SecurityEquivalenceInSecuritySet(TypedDict, total=False):
    securitySetId: int
    securityId: int
    equivalentSecurityId: int
    relatedType: int
    relatedTypeId: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    rank: int
    doNotTLH: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isDeleted: int


class SecuritySet(TypedDict, total=False):
    id: int
    name: str
    description: str
    isDynamic: bool
    isFavorite: bool
    toleranceType: int
    toleranceTypeValue: float
    isDeleted: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isCommunityModel: bool
    overrideStrategistUpdates: bool
    altsManagedByStrategist: bool
    allowAlternativeToleranceBands: bool
    details: list[SecuritySetDetail]


class SecuritySetAlternative(TypedDict, total=False):
    securitySetId: int
    securityId: int
    custodianId: int
    equivalentSecurityId: int
    relatedType: int
    relatedTypeId: int
    taxableSecurityId: int
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredSecurityId: int
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptSecurityId: int
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class SecuritySetDetail(TypedDict, total=False):
    securitySetId: int
    securityId: int
    rank: int
    targetPercent: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int
    lowerModelToleranceAmount: float
    upperModelToleranceAmount: float
    doNotTLH: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isDeleted: int
    security: Security
    securityTlhInSecuritySets: list[SecurityTLHInSecuritySet]
    securityEquivalenceInSecuritySets: list[SecurityEquivalenceInSecuritySet]
    securitySetAlternatives: list[SecuritySetAlternative]


class SecurityTLHInSecuritySet(TypedDict, total=False):
    securitySetId: int
    securityId: int
    custodianId: int
    tlhSecurityId: int
    priority: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isDeleted: bool
    isSecuritySetLevel: bool


class AccountSetAsideCash(TypedDict, total=False):
    id: int
    description: str
    cashAmountType: int
    cashAmount: float
    expirationType: int
    expireDate: str
    expireTransactionType: int
    systemExpiredOn: str
    isDeleted: bool
    minCashAmount: float
    minCashAmountType: int
    percentCalculationTypeId: int
    setAsideAccountTypeId: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    maxCashAmount: float
    isSystematic: bool
    startDate: str
    isBilling: bool
    isDepleteOverTime: bool
    initialAmount: float
    initialMinSetAside: float
    initialMaxSetAside: float
    accountId: int
    account: Account
    portfolioSetAsideCashId: int
    transactionAmountTolerance: float


class SleeveContributionMethod(TypedDict, total=False):
    id: int
    contributionMethodName: str
    contributionMethodValue: int
    isDeleted: bool
    contributionMethodDisplayName: str


class SleeveDistributionMethod(TypedDict, total=False):
    id: int
    distributionMethodName: str
    distributionMethodValue: int
    isDeleted: bool
    distributionMethodDisplayName: str


class PortfolioSummaryAccount(TypedDict, total=False):
    accountId: int
    modelId: int
    modelName: str
    sleeveStrategyName: str
    custodialAccountNumber: str
    modelManagementStyle: str
    orionConnectFirmId: int


class RankedTaxLots(TypedDict, total=False):
    taxLotId: int
    accountNumber: str
    accountId: int
    accountName: str
    isDoNotBuySell: bool
    isExcludedSecurity: bool
    custodian: str
    taxableType: str
    isSMA: bool
    billingAccount: bool
    restrictedPlanName: str
    securityId: int
    symbol: str
    securityName: str
    cusip: str
    dateAcquired: str
    quantity: float
    pendingQuantity: float
    costAmount: float
    costPerShare: float
    taxLotPrice: float
    marketValue: float
    pendingMarketValue: float
    securityPrice: float
    priceDate: str
    securityType: str
    securityTypeId: int
    isLongTerm: bool
    stUnrealizedGainLoss: float
    stLotUnrealizedGainLossPercent: float
    stHoldingUnrealizedGainLossPercent: float
    ltUnrealizedGainLoss: float
    ltLotUnrealizedGainLossPercent: float
    ltHoldingUnrealizedGainLossPercent: float
    unrealizedGainLoss: float
    lotUnrealizedGainLossPercent: float
    holdingUnrealizedGainLossPercent: float
    rank: int
    isCash: bool
    isSettled: bool
    acquiredDays: float
    tradeQuantity: float
    productCategoryName: str
    productClassName: str
    productSubClassName: str
    originalQuantity: float
    isTradableMoneyMarket: bool
    depletionMethod: str


class TacticalPortfolioSummary(TypedDict, total=False):
    id: int
    name: str
    managedValue: float
    excludedValue: float
    outOfTolerance: int
    tradingInstructions: str
    notesCount: int
    displayNotes: str
    teamDisplayNotes: str
    tags: str
    team: str
    teamId: str
    lastRebalancedOn: str
    lastTradedDate: str
    yearToDateGain: float
    maxGainAmount: str
    carryForwardLoss: str
    tradeApprovalLevels: str
    modelId: int
    modelName: str
    substitutedModelId: int
    substitutedModelName: str
    rebalanceLevel: str
    needsAnalytics: int
    failedReason: str
    analyticsEditedDate: str
    isSleevePortfolio: int
    allowWashSales: int
    equivalentDistributionMethod: str
    ordinaryIncomeTax: float
    longTermCapitalGainTax: float
    doNotTrade: bool
    autoRebalance: bool
    nextAutoRebalanceDate: str
    rebalanceDay: int
    rebalanceOptionId: int
    rebalanceOption: str
    rebalanceTypeId: int
    rebalanceType: str
    reviewLevel: str
    includeLevelsAboveReview: int
    secondaryTeams: list[Team]
    sleeveStrategyAggregateName: str
    contributionAmount: float
    accounts: list[PortfolioSummaryAccount]
    hasTaxLossHarvest: bool
    orionConnectFirmId: int
    registrationId: int
    sleevePortfolioRebalanceLevel: str
    maxShortTermGain: float
    hasContribution: bool
    hasDistribution: bool
    discretionaryTrade: bool


class TacticalRestrictedSecurity(TypedDict, total=False):
    securityId: int
    symbol: str
    status: str
    level: str
    portfolioId: int
    accountId: int


class GetTlhOpportunityFlagDto(TypedDict, total=False):
    ids: list[int]
    type: str


class GetTlhOpportunityFlagResponseDto(TypedDict, total=False):
    id: int
    hasTaxLossHarvest: bool


class Trading_OrderStatus(TypedDict, total=False):
    id: int
    name: str
    value: str
    isDeleted: bool
    createdBy: int
    createdDate: str
    editedBy: int
    editedDate: str
    trades: list[Trade]


class SellTradeLots(TypedDict, total=False):
    id: int
    tradesId: int
    taxLotId: int
    quantity: float
    dateAcquired: str
    costPerShare: float
    isLongTerm: int
    taxlotTypeId: int
    blockId: int
    trade: Trade
    origTaxlotQuantity: float


class Trade(TypedDict, total=False):
    id: int
    portfolioId: int
    securityId: int
    accountId: int
    tradeOrderMessageId: int
    tradeInstanceId: int
    instanceId: int
    custodianId: int
    positionId: int
    modelId: int
    advisorId: int
    severity: int
    tradeAmount: float
    tradeCode: int
    status: str
    createdDate: str
    isEnabled: bool
    orderQty: float
    orderPercent: float
    price: float
    warningMessage: str
    tradingInstructions: str
    createdBy: int
    editedBy: int
    editedDate: str
    isDeleted: bool
    cashValuePostTrade: float
    orderTypeId: int
    limitPrice: float
    stopPrice: float
    qualifierId: int
    durationId: int
    isDiscretionary: int
    isSolicited: bool
    isAutoAllocate: int
    tradeActionId: int
    approvalStatusId: int
    holdUntil: str
    accountValue: float
    blockId: int
    calculationMethodId: int
    cashValue: float
    instanceNotes: str
    reinvestDividends: bool
    reinvestLongTermGains: bool
    reinvestShortTermGains: bool
    settlementTypeId: int
    assetId: int
    assetUnits: int
    hasBlock: bool
    notes: str
    originalOrderQty: float
    rebalanceLevelId: int
    timeInForceId: int
    transactionId: int
    isClientDirected: bool
    vspDate: str
    vspPrice: float
    orderStatusId: int
    allocationStatusId: int
    tradeFileId: int
    daysUntilLongTerm: int
    expireTime: str
    fullSettDate: str
    isLocateRequired: bool
    marketValue: float
    rowVersion: int
    totalGain: float
    tradePercentageOfAccount: float
    minCashBalance: float
    isTransactionFeeIncluded: bool
    isSendImmediately: bool
    isTLH: bool
    redemptionFee: float
    transactionFee: float
    handlInstId: int
    execInst: str
    tradeTypeId: int
    isTradeable: bool
    vspInfo: int
    sellSharesThreshold: int
    reinvestCapitalGains: bool
    nettingQuantity: float
    nettingBlockId: int
    isMac: int
    mutualFundSell: str
    washUnits: float
    washAmount: float
    partialShares: int
    houseAccountOrder: bool
    parentTradeId: int
    isFixedIncomeTrade: int
    optionExecutionType: int
    optionMaturityDate: str
    optionParentProduct: str
    optionType: int
    strikePrice: float
    optionTradesLinkId: str
    orderLocation: str
    tradeInstance: TradeInstance
    custodian: Custodian
    portfolio: Portfolio
    orderStatus: Trading_OrderStatus
    security: Security
    account: Account
    sellTradeLots: list[SellTradeLots]
    error: list[TradeOrderMessageAssn]
    advisor: Advisor
    tradeBlock: TradeBlock
    orderConditionTypeId: int
    astroTradeId: int


class TradeBlock(TypedDict, total=False):
    id: int
    tradeActionId: int
    orderQuantity: float
    securityId: int
    estimateAmount: float
    orderStatusId: int
    orderTypeId: int
    limitPrice: float
    cumQty: float
    leavesQty: float
    avgPrice: float
    blockRejectReasonId: int
    createdBy: int
    createdDate: str
    editedBy: int
    editedDate: str
    custodianId: int
    isAutoAllocate: bool
    blockAllocationRejectId: int
    allocationId: str
    blockCancelRejectReasonId: int
    cfiCodeId: int
    durationId: int
    execInst: str
    expireTime: str
    clOrderId: str
    fullSettDate: str
    handlInstId: int
    lastPrice: float
    lastShare: float
    lastText: str
    lastTextTypeId: int
    maturityDate: str
    messageSequenceNumber: int
    blockOrderCapacity: int
    orderId: str
    pendingOrderStatusId: int
    blockPositionEffectId: int
    qualifierId: int
    settlementTypeId: int
    isSolicited: bool
    stopPrice: float
    strikePrice: float
    tradedBy: int
    transactionTime: str
    portfolioId: int
    isDeleted: bool
    allocationStatusId: int
    isDiscretionary: bool
    execTypeId: int
    originalClOrderId: str
    executingBrokerId: int
    executingDestinationId: int
    allocationDestinationId: int
    tradeAwayBlockId: int
    isTradeAwayBlock: bool
    custodianAlgoTagId: int
    algoInstruction: str
    parentBlockId: int
    trades: list[Trade]
    isUnderlyingCustodian: bool


class TradeInstance(TypedDict, total=False):
    id: int
    description: str
    createdDate: str
    createdBy: int
    createdByUser: User
    editedDate: str
    editedBy: int
    userId: int
    tradeCreationStatusId: int
    tradeParameter: str
    tradeStartTime: str
    tradeEndTime: str
    errorMessage: str
    notes: str
    tradingAppId: int
    tradeInstanceType: int
    tradeInstanceSubType: int
    tradeToolSelection: int
    entityCount: int
    isEnabled: bool
    isDeleted: bool
    errorPortfolioStatus: str
    errorPortfolioCount: int
    queuedStatus: int
    trades: list[Trade]
    outsourcedManager: str


class TradeOrderMessage(TypedDict, total=False):
    id: int
    severityId: int
    shortCode: str
    message: str


class TradeOrderMessageAssn(TypedDict, total=False):
    id: int
    tradeId: int
    tradeOrderMessageId: int
    tradeOrderMessage: TradeOrderMessage
    messageArguments: str


class ModelAllocationChangeDto(TypedDict, total=False):
    ticker: str
    productName: str
    currentAllocation: float
    currentLowerTolerance: float
    currentUpperTolerance: float
    currentAlts: str
    requestedAllocation: float
    requestedLowerTolerance: float
    requestedUpperTolerance: float
    requestedAlts: str


class TradeQueueDetailDto(TypedDict, total=False):
    commentary: str
    allocationChanges: list[ModelAllocationChangeDto]


class ComplianceAccountDto(TypedDict, total=False):
    id: int
    accountType: str
    accountValue: float
    accountPostTradeHoldingPercent: float
    cashValue: float
    cashValuePostTrade: float
    cashValuePostTradePercent: float
    holdingUnits: float


class CompliancePortfolioDto(TypedDict, total=False):
    id: int
    name: str
    cashTolerance: str
    tolerance: str
    managedValue: float
    postTradeHoldingPercent: float
    totalValue: float
    tags: str


class ComplianceSecurityDto(TypedDict, total=False):
    id: int
    identifier: str
    instrument: str
    isin: str
    securityType: str
    price: float


class ComplianceTradeRequestDto(TypedDict, total=False):
    tradesId: str
    alClientId: int
    firmId: int
    tradeIdentityUuid: str
    requestId: int
    teamId: int
    modelId: int
    action: str
    amount: float
    custodian: str
    managementStyle: str
    marketValue: float
    orderType: str
    quantity: float
    tradePercentOfAccount: float
    tradePercentOfPortfolio: float
    washAmount: float
    washUnits: float
    account: ComplianceAccountDto
    portfolio: CompliancePortfolioDto
    security: ComplianceSecurityDto
    trader: ComplianceTraderDto
    brokerDealerId: int
    riaId: int


class ComplianceTraderDto(TypedDict, total=False):
    id: int
    firstName: str
    lastName: str
    email: str
    tags: str


class TradeAppealAndOverrideRequestDto(TypedDict, total=False):
    alClientId: int
    firmId: int
    tradeIdentityUuid: str
    requestId: int
    reason: str
    requestedBy: str
    brokerDealerId: int
    riaId: int


class TradeAppealAndOverrideResponseDto(TypedDict, total=False):
    message: str
    isError: bool
    complianceStatus: str
    requestId: str


class TradeEnqueueRequestDto(TypedDict, total=False):
    tradeInstanceId: int
    eclipseFirmId: int
    requestId: int


class TradeEnqueueResponseDto(TypedDict, total=False):
    processId: str


class TradeReviewResponseDto(TypedDict, total=False):
    tradeIdentityUuid: str
    submitDate: str
    status: str
    reviewMessage: str
    requestId: str
    reviewDate: str


class AccountTagsDto(TypedDict, total=False):
    id: int
    tags: str


class ProfileDto(TypedDict, total=False):
    id: int
    loginEntityId: int
    entityId: int
    advisorName: str
    entityName: str
    roleId: int
    isUserDefault: bool
    alClientId: int
    roleName: str
    isInCurrentDb: bool
    entity: int


class RepUserDto(TypedDict, total=False):
    userId: str
    firstName: str
    lastName: str
    email: str
    id: int
    isActive: bool
    entityName: str
    isReset: bool
    profiles: list[ProfileDto]


class SetAsideCashExpiringTransactionsDto(TypedDict, total=False):
    amountExpired: float
    expiringDate: str
    initialMaxSetAside: float
    initialCashAmount: float
    initialMinSetAside: float
    transactionAmount: float


class EntityOption(TypedDict, total=False):
    userDefineDataId: int
    value: str
    entity: int
    entityId: int
    entityName: str
    userDefineDefinitionId: int
    name: str
    category: str
    type: str
    code: str
    sequence: int
    options: Any
    input: str
    securityCode: str
    canEdit: bool


class SleeveStrategy(TypedDict, total=False):
    id: int
    name: str
    contributionAllocationMethod: int
    distributionAllocationMethod: int
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    autoRebalFreq: int
    autoRebalMonth: int
    autoRebalDay: int
    mandate: bool
    tolerancePercent: float
    hasAssignedRegistrations: bool
    entityId: int
    entity: int
    riskScore: float
    originalRiskScore: float
    sleeveStrategyRiskTypeId: int
    include: bool
    useRestrictions: bool
    owned: bool
    orionConnectFirmId: int
    firmId: int


class SleeveStrategyAggregate(TypedDict, total=False):
    id: int
    name: str
    contributionAllocationMethod: int
    distributionAllocationMethod: int
    autoRebalFreq: int
    autoRebalMonth: int
    autoRebalDay: int
    entityId: int
    entity: int
    createdDate: str
    createdBy: str
    auditedDate: str
    auditedByDisplay: str
    grouping: str
    singleStrategyId: int
    sleeveStrategyCount: int
    orionConnectFirmId: int
    firmId: int


class AccountSetAsideCashResponseDto(TypedDict, total=False):
    id: int
    accountId: int
    accountNumber: str
    setAsideCashAmountType: int
    setAsideCashAmount: float
    minCashAmount: float
    maxCashAmount: float
    transactionAmountTolerance: float
    setAsidePercentCalculationTypeId: int
    isActive: bool
    expirationValue: str
    expirationTypeId: int
    expirationType: str
    createdOn: str
    createdBy: str
    editedOn: str
    editedBy: str
    expiredOn: str
    expiredBy: str
    cashAmountTypeId: int
    cashAmountType: str
    description: str
    startDate: str
    setAsideAccountTypeId: int
    setAsideAccountType: str


class OrionAdvisorNumberDto(TypedDict, total=False):
    entityId: int
    userDefineDefinitionId: int
    userDefineDataId: int
    value: str
    description: str
    securityCode: str
    definition: str


class OrionReportSearchDto(TypedDict, total=False):
    id: str
    name: str


class OrionServiceTeamResponseDto(TypedDict, total=False):
    chatRouteIntendedRecipient: str
    chatUrl: str
    emailAddress: str
    firmChatRouteId: str
    id: int
    phone: str
    team: str


class QuoddStatusDto(TypedDict, total=False):
    registrationStatus: int
    isRegistered: bool


class RealTimePriceResponseDto(TypedDict, total=False):
    marketClosePrice: float
    date: str
    last: float
    symbol: str
    isRealTimeQuote: bool
    isDelayedQuote: bool
    changeFromLastClose: float
    changeFromLastMarketClose: float
    changeFromMarketClose: float
    changeFromMarketOpen: float
    changeFromPrev: float
    lastClosePrice: float
    lastMarketClosePrice: float
    marketOpenPrice: float
    percentChangeFromLastClose: float
    percentChangeFromLastMarketClose: float
    percentChangeFromMarketClose: float
    percentChangeFromMarketOpen: float
    percentChangeFromOpen: float
    percentChangeFromPrev: float
    ask: float
    askQuantity: float
    bid: float
    bidQuantity: float
    changeFromOpen: float
    changeFromPrevious: float
    cusip: str
    delay: float
    high: float
    low: float
    name: str
    outcome: str
    percentageChangeFromOpen: float
    percentageChangeFromPrevious: float
    quantity: float
    volume: float
    open: float
    eclipsePriceSource: str
    registrationStatus: int
    registrationStatusMessage: str
    canSeeDetailedQuotePriceFields: bool
    averageThirtyDayVolume: str


class TradeExecutionTypeDto(TypedDict, total=False):
    id: int
    name: str
    transmitMethod: bool
    fileGeneratorEnum: int
    custodianGroupId: int
    isDeleted: int


class AccountCashDetailsDto(TypedDict, total=False):
    distributionAmount: float
    contributionAmount: float
    cashPer: float
    cashValue: float
    cashTargetPercent: float
    targetCash: float
    cashNeedPercentage: float
    cashNeedAmount: float
    targetSetAsideCash: float
    actualSetAsideCash: float
    minSetAsideCash: float
    maxSetAsideCash: float
    managedCashValue: float
    managedCashPercent: float


class AccountDetailDto(TypedDict, total=False):
    id: int
    accountId: str
    isDoNotBuySell: bool
    isCustodialRestriction: bool
    restrictedPlanId: int
    connectFirmId: int
    connectAccountId: int
    astroSetting: AstroSetting
    tags: str
    rebalanceOptionId: int
    rebalanceDay: int
    setForAutoRebalance: bool


class AccountDetailResponseDto(TypedDict, total=False):
    id: int
    macStatus: int
    orionConnectFirmId: int
    needAnalyticsStatus: str
    accountId: str
    name: str
    accountNumber: str
    portfolio: str
    portfolioId: int
    custodian: str
    washSaleGroup: str
    model: str
    modelId: int
    style: str
    billingAccount: str
    advisor: str
    sleeveType: str
    createdOn: str
    createdBy: str
    editedOn: str
    editedBy: str
    registrationId: int
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    sleeveTarget: float
    sleeveToleranceLower: float
    sleeveToleranceUpper: float
    smaTradeable: str
    sleeveCureent: float
    sleeveCurrent: float
    orionConnectExternalId: int
    accountType: str
    isSleeve: int
    isDisabled: int
    instructions: str
    isDoNotBuySell: bool
    isCustodialRestriction: bool
    tradingInstruction: str
    restrictedPlanId: int
    restrictedPlanName: str
    astroEnabled: bool
    excludeRebalanceSleeve: str
    sleeveStrategyId: str
    sleeveStrategyName: str
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    isMultiAssetClass: bool
    subAdvisorName: str
    yearToDateGainLoss: YearToDateGainLoss
    accountValue: AccountValue
    errorAndWarnings: Errors
    summarySection: Summary
    entityOptions: list[EntityOption]
    tags: str
    postTradeNeedPercent: float
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float
    setForAutoRebalance: bool
    rebalanceOptionId: int
    rebalanceDay: int
    rebalanceType: str
    lastTradedDate: str
    lastRebalancedDate: str
    lastOptimizedDate: str
    lastTLHDate: str
    nextAutoRebalanceDate: str
    hasTaxLossHarvest: bool
    contributionAmount: float
    distributionAmount: float
    cashNeedAmount: float
    cashNeedPercent: float
    portfolioCashOutOfTolerance: bool
    portfolioOutOfTolerance: bool
    outsourcedStatus: str
    companionEclipseFirmName: str
    teams: list[AccountDetailResponse_Team]


class AccountValue(TypedDict, total=False):
    totalValueOn: str
    totalValue: float
    status: str
    holdings: list[Holding]


class Errors(TypedDict, total=False):
    systematic: str
    mergeIn: float
    mergeOut: float
    newAccount: str
    hasPortfolios: str
    custodialRestrictions: str
    sma: str
    importError: str
    hasPendingTrades: str
    setForAutoRebalance: bool


class Holding(TypedDict, total=False):
    securityName: str
    securitySymbol: str
    marketValue: float
    unit: float
    price: float
    percentage: float
    pendingValue: float


class Summary(TypedDict, total=False):
    grandTotal: float
    totalValue: float
    managedValue: float
    excludedValue: float
    totalCashValue: float
    cashReserve: float
    cashAvailable: float
    setAsideCash: float
    pendingCashValue: float


class AccountDetailResponse_Team(TypedDict, total=False):
    name: str
    isPrimaryTeam: bool


class YearToDateGainLoss(TypedDict, total=False):
    totalGainLoss: float
    totalGainLossStatus: str
    shortTermGainLoss: float
    shortTermGainLossStatus: str
    longTermGainLoss: float
    longTermGainLossStatus: str


class AccountGainLossSummaryDto(TypedDict, total=False):
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedTotalGain: float
    unRealizedLongTermGain: float
    unRealizedShortTermGain: float
    unRealizedTotalGain: float


class AccountHistoryDto(TypedDict, total=False):
    portfolioId: int
    portfolioName: str
    modelId: int
    modelName: str
    astroEnabled: str
    isDoNotBuySell: str
    changeType: str
    createdDate: str
    editedDate: str
    createdBy: str
    editedBy: str
    tags: str
    restrictedPlan: str


class AccountListDto(TypedDict, total=False):
    id: int
    accountNumber: str
    accountId: str
    orionConnectExternalId: int
    orionConnectFirmId: int
    portfolio: str
    portfolioId: int
    portfolioGroupId: int
    custodian: str
    value: float
    managedValue: float
    excludedValue: float
    pendingValue: float
    washSaleGroup: str
    style: Any
    model: str
    sleeveType: str
    distributionAmount: float
    contributionAmount: float
    mergeIn: float
    mergeOut: float
    cashNeedAmount: float
    systematicAmount: float
    systematicDate: str
    sma: int
    pendingTrades: int
    eclipseCreatedDate: str
    reserveCashTarget: float
    setAsideCashTarget: float
    setAsideCashActual: float
    targetCash: float
    targetCashPercent: float
    currentCash: float
    currentCashPercent: float
    pendingCashValue: float
    pendingCashPercent: float
    cashNeedPercent: float
    pendingValuePercent: float
    isDisabled: int
    restrictedPlanId: Any
    restrictedPlanName: str
    createdBy: str
    editedBy: str
    isMAC: int
    astroEnabled: int
    shortTermTaxRate: float
    longTermTaxRate: float
    ticketCharge: float
    maxCapGains: float
    currentTrackingError: float
    maxTrackingError: float
    astroTemplateId: str
    lastOptimizedDate: str
    status: str
    unrealizedGain: float
    unrealizedLoss: float
    taxQualification: str
    team: str
    createdOn: str
    editedOn: str
    excludeRebalanceSleeve: str
    portfolioTolerance: str
    portfolioCashTolerance: str
    tradingInstructions: str
    representativeName: str
    isOptionTradingAllowed: bool
    sleeveStrategyId: str
    sleeveStrategyName: str
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    hasOptionsExpiringSoon: bool
    subAdvisorName: str
    lastRebalancedOn: str
    lastTradedDate: str
    registrationId: int
    portfolioDoNotTrade: bool
    minSetAsideCash: float
    maxSetAsideCash: float
    tags: str
    doNotTrade: str
    isDiscretionary: str
    managementStyle: str
    accountTags: str
    householdName: str
    representativeNumber: str
    outsideId: str
    secondaryAccountNumber: str
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedGain: float
    businessLine: str
    hasTLH: bool
    sleeveCurrentPercent: float
    sleeveTargetPercent: float
    sleeveNeedPercent: float
    needAnalyticsStatus: str
    billPayMethod: str
    inBalance: bool
    downloadSource: str
    hasUnassignedHoldings: bool
    notesCount: int
    displayNotes: str
    numberOfAccounts: int
    teamNotes: str
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    lastPositionDate: str
    modelTags: str
    reserveCashActual: float
    accountType: str
    name: str
    reason: str


class AccountListDynamicDto(TypedDict, total=False):
    id: int
    accountNumber: str
    accountId: str
    accountModelId: int
    portfolio: str
    portfolioId: int
    portfolioGroupId: int
    portfolioModelId: int
    custodian: str
    value: float
    managedValue: float
    excludedValue: float
    pendingValue: float
    washSaleGroup: str
    style: Any
    modelId: int
    model: str
    sleeveType: str
    distributionAmount: float
    contributionAmount: float
    mergeIn: float
    mergeOut: float
    cashNeedAmount: float
    systematicAmount: float
    systematicDate: str
    sma: int
    pendingTrades: int
    eclipseCreatedDate: str
    reserveCashTarget: float
    setAsideCashTarget: float
    setAsideCashActual: float
    targetCash: float
    targetCashPercent: float
    currentCash: float
    currentCashPercent: float
    pendingCashValue: float
    pendingCashPercent: float
    cashNeedPercent: float
    pendingValuePercent: float
    isDisabled: int
    restrictedPlanId: Any
    restrictedPlanName: str
    createdBy: str
    editedBy: str
    isMAC: int
    astroEnabled: int
    shortTermTaxRate: float
    longTermTaxRate: float
    ticketCharge: float
    maxCapGains: float
    currentTrackingError: float
    previousDayTrackingError: float
    maxTrackingError: float
    maxTrackingErrorDifference: float
    astroTemplateId: str
    lastOptimizedDate: str
    status: str
    unrealizedGain: float
    unrealizedLoss: float
    taxQualification: str
    team: str
    createdDate: str
    editedDate: str
    excludeRebalanceSleeve: str
    portfolioTolerance: str
    cashOutOfTolerance: str
    sleeveToleranceStatus: str
    tradingInstructions: str
    representativeName: str
    isOptionTradingAllowed: bool
    sleeveStrategyId: str
    sleeveStrategyName: str
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    subAdvisorName: str
    hasOptionsExpiringSoon: bool
    accountTypeName: str
    accountName: str
    statusReason: str
    reserveCashActual: float
    needAnalytics: int
    lastRebalancedOn: str
    lastTradedDate: str
    registrationId: int
    portfolioDoNotTrade: bool
    minSetAsideCash: float
    maxSetAsideCash: float
    tags: str
    doNotTrade: str
    isDiscretionary: str
    managementStyle: str
    accountTags: str
    representativeNumber: str
    householdName: str
    outsideId: str
    secondaryAccountNumber: str
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedGain: float
    businessLine: str
    hasTLH: bool
    sleeveCurrentPercent: float
    sleeveTargetPercent: float
    sleeveNeedPercent: float
    needAnalyticsStatus: str
    billPayMethod: str
    inBalance: bool
    downloadSource: str
    hasUnassignedHoldings: bool
    notesCount: int
    displayNotes: str
    numberOfAccounts: int
    teamNotes: str
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    setAsideCashCount: int
    outputColumns: list[str]
    postTradeNeedPercent: float
    lastPositionDate: str
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    modelTags: str
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float
    modelDeviationPercent: float
    lastTLHDate: str
    astroLastTLHDate: str
    sweepCash: float
    sweepCashPercent: float
    moneyMarketCash: float
    moneyMarketCashPercent: float
    outsourcedStatus: str
    companionEclipseFirmId: int
    companionEclipseFirmName: str
    orionConnectFirmId: int
    orionConnectExternalId: int
    autoRebalanceType: str
    nextAutoRebalanceDate: str
    representativeId: int
    depletionMethod: str
    tradingBlocksCount: int
    tradingBlocks: str
    gainBudgetRemaining: float
    accountStatus: str
    orionConnectFirmName: str
    managed: str
    managedCash: float
    mutualFundDepletionMethod: str
    managedCashPercent: float
    maxGainAmount: float
    rmdAmount: float
    rmdRemaining: float
    distributionAmtYTD: float
    accountCashOutOfTolerance: str


class AccountModelHistoryDto(TypedDict, total=False):
    changeType: str
    modelId: int
    modelName: str
    editedDate: str
    editedBy: str
    astroEnabled: str
    sma: str
    modelSubstituted: str


class AccountSetAsideTransactionsDto(TypedDict, total=False):
    transactionId: int
    transactionExternalId: int


class AccountSimpleDto(TypedDict, total=False):
    id: int
    accountId: str
    accountNumber: str
    name: str
    portfolioId: int
    value: float
    accountType: str


class AccountSmaAllocationDto(TypedDict, total=False):
    id: int
    accountId: int
    modelId: int
    modelDetailId: int
    weightPercent: float
    subModelId: int
    levelId: int


class AccountTransactionDto(TypedDict, total=False):
    status: str
    transDate: str
    transAmount: float
    navPrice: float
    id: int
    transactionDescription: str
    productName: str
    ticker: str
    noUnits: float
    accountNumber: str
    type: str
    transTime: str
    assetId: int
    assetStatusId: int
    cusip: str
    notes: str
    transTypeId: int
    transactionSubTypeId: int
    transactionSubTypeName: str
    transactionSubTypeDescription: str
    contributionCodeId: str
    contributionCodeName: str
    distributionCodeId: str
    distributionCodeName: str
    accountId: int
    accountStatusId: int
    managementStyle: str
    payee: str
    advisorNotes: str
    state: str
    settleDate: str
    tradeReferenceNumber: str
    transactionLinkCode: str
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    registrationId: int
    clientId: int
    typeCode: str
    brokerCode: str
    accountType: str
    fundFamily: str
    custodian: str
    count: int
    registrationName: str
    unitBalance: float
    productId: int
    performanceFeeBreak: bool
    financialType: str


class AstroAccountDto(TypedDict, total=False):
    id: int
    accountId: str
    name: str
    accountNumber: str
    model: str
    currentCash: float
    value: float
    astroEnabled: bool
    orionConnectExternalId: int
    orionConnectFirmId: int
    hasTrackingErrorAlert: bool
    hasRiskAlert: bool
    hasTaxLossHarvestingOpportunities: bool
    hasCashAlert: bool
    hasNewTemplateAssignmentAlert: bool
    currentTrackingError: float
    minTrackingError: float
    maxTrackingError: float
    riskTolerance: float
    riskToleranceTarget: float
    riskToleranceMin: float
    riskToleranceMax: float
    cashMinPer: float
    cashPer: float
    cashMaxPer: float
    taxLossHarvestingAmount: float
    lastOptimizedDate: str
    isDisabled: int


class AstroSetting(TypedDict, total=False):
    astroEnabled: bool
    strategyName: str
    eclipseModelId: int
    createdByOciProcess: bool


class ExpireAccountSetAsidesAndTransactionsDto(TypedDict, total=False):
    setAsideId: int
    setAsideTransactions: list[AccountSetAsideTransactionsDto]


class AnalyticsStatusUpdateRequest(TypedDict, total=False):
    percentageCompleted: int
    instanceId: int
    timedOutPortfolioIds: list[int]
    durationSchedulerId: str
    trigger: str
    errorMessage: str
    requestedById: str
    correlationId: str


class PortfolioAnalyticsFlagDto(TypedDict, total=False):
    portfolioId: int
    needAnalytics: int
    failedReason: str
    editedDate: str


class RunAnalyticsConfigDto(TypedDict, total=False):
    id: int
    processTrigger: str
    launchAnalytics: bool
    requiredForTrading: bool
    displayName: str
    editedBy: int
    editedDate: str
    readOnly: bool


class RunAnalyticsRequest(TypedDict, total=False):
    portfolioIds: list[int]
    runFullAnalytics: bool
    filterOnNeedsAnalyticsOnly: bool
    correlationId: str
    filterByCorrelationId: bool
    trigger: str
    startDate: str
    requestedById: str
    isScheduled: bool


class UserSecurityClassificationGroupDto(TypedDict, total=False):
    id: int
    name: str
    isPublic: bool
    securityClassificationMethods: str
    ownedBy: int
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class CustodianAlgoInstructionDto(TypedDict, total=False):
    id: int
    custodianAlgoTagInfoId: int
    instruction: str


class CustodianAlgoTagInfoDto(TypedDict, total=False):
    id: int
    custodianId: int
    tag: str
    algoName: str
    algoInstruction: str
    rangeFromValue: int
    rangeToValue: int
    customFixTags: list[CustomFixTagDefinitionDto]


class CustodianAllocationInstructionDto(TypedDict, total=False):
    id: int
    code: str
    name: str


class CustodianDetailDto(TypedDict, total=False):
    id: int
    name: str
    code: str
    accountNumber: str
    routing: str
    fixVersion: str
    fixBankId: str
    defaultTradeExecutionTypeId: int
    tradeExecutions: list[TradeExecutionDto]
    houseAccount: HouseAccountDto
    allowFractionalEquityOrder: bool
    fractionalEquityPrecision: int
    tdaUserId: str
    tdaNamespace: str
    allocationMethod: int
    isAllowTradeAway: bool
    commissions: float
    fees: float
    isDisableFixBlockRounding: bool
    executingBrokerId: int
    allocationDestinationId: int
    allocationInstructionId: int
    customAllocationMessage: str
    mpid: str
    allowOnlyCreateFractionalShareLiquidationTrades: bool
    isSendOrderCondition: bool
    isSendBrokerAllocationMessage: bool
    custodianExecutionSettings: list[CustodianExecutionSettingDto]


class CustomFixTagDefinitionDto(TypedDict, total=False):
    id: int
    customTagType: int
    custodianId: int
    custodianAlgoTagInfoId: int
    broker: str
    displayName: str
    algoType: str
    fixTag: int
    dataType: int
    minimumValue: float
    maximumValue: float
    decimalPrecision: int
    required: bool
    enumPairs: list[EnumPairDto]
    defaultValue: str
    displayOrder: int


class EnumPairDto(TypedDict, total=False):
    label: str
    value: str
    displayOrder: int


class HouseAccountDto(TypedDict, total=False):
    id: str
    accountId: str
    accountNumber: str
    name: str


class OutsourcedTradeExecutionFirmOverrideDto(TypedDict, total=False):
    connectFirmId: int
    connectFirmName: str
    securityTypeId: int


class TradeExecutionDto(TypedDict, total=False):
    securityTypeId: int
    securityTypeName: str
    tradeExecutionTypeId: int
    tradeExecutionTypeName: str
    allocationTradeExecutionTypeId: int
    allocationTradeExecutionTypeName: str
    selectedOutsourcedTradeExecutionFirmOverride: list[int]
    isAllowTradingAway: int
    executionDestinationId: int
    allocationDestinationId: int
    executionDestinationTypeId: int


class CustomImportInstanceStatusDto(TypedDict, total=False):
    instanceId: int
    importStatusId: int
    importStatus: str
    importName: str
    overrideInstanceId: int
    importType: str
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    template: CustomImportTemplateDto


class CustomImportTemplateColumnDto(TypedDict, total=False):
    id: int
    columnName: str
    displayName: str
    dataType: str
    displayOrder: int
    isRequired: bool
    isHeader: bool
    hint: str
    validValues: CustomImportTemplateColumnValidValuesDto


class CustomImportTemplateColumnValidValueSetDto(TypedDict, total=False):
    value: str
    aliases: list[str]


class CustomImportTemplateColumnValidValuesDto(TypedDict, total=False):
    validValues: list[CustomImportTemplateColumnValidValueSetDto]
    deleteIdentifiers: list[str]


class CustomImportTemplateDto(TypedDict, total=False):
    id: int
    templateName: str
    isUserFavorite: bool
    fullFilename: str
    isOverridable: bool
    columns: list[CustomImportTemplateColumnDto]


class CustomImportUserPreferenceDto(TypedDict, total=False):
    userId: int
    templateId: int
    isFavorite: bool


class AccountDashboardAccountsDto(TypedDict, total=False):
    total: int
    existing: int
    new: int
    astro: int


class AccountDashboardBarsDto(TypedDict, total=False):
    systematic: int
    accountWithMergeIn: int
    accountWithMergeOut: int
    newAccount: int
    accountWithNoPortfolio: int
    toDo: int
    sma: int
    accountWithDataError: int
    accountWithPendingTrade: int
    astroWithTrackingErrorOutOfTolerance: int
    astroWithRiskOutOfTolerance: int
    astroWithTaxLossHarvestingOpportunities: int
    astroWithCashOutOfTolerance: int
    astroWithNewTemplateAssignments: int
    optionTradingOpportunities: int
    optionsExpiringSoon: int


class AccountDashboardIssuesDto(TypedDict, total=False):
    total: int
    errors: int
    warnings: int


class AccountDashboardSummaryDto(TypedDict, total=False):
    dateTime: str
    value: AccountDashboardValueDto
    accounts: AccountDashboardAccountsDto
    issues: AccountDashboardIssuesDto
    bars: AccountDashboardBarsDto


class AccountDashboardValueDto(TypedDict, total=False):
    total: float
    changeValueAmount: float
    changeValuePercent: float
    status: str


class DashboardCategoryDto(TypedDict, total=False):
    id: int
    name: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int


class DashboardDetailDto(TypedDict, total=False):
    id: int
    dashboardFieldId: int
    userGridViewId: int
    dashboardId: int
    displayIndex: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    dashboardField: DashboardFieldDto
    userGridView: UserGridViewSlimDto


class DashboardDto(TypedDict, total=False):
    id: int
    userId: int
    teamId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    dashboardDetails: list[DashboardDetailDto]


class DashboardFieldDto(TypedDict, total=False):
    id: int
    dashboardCategoryId: int
    displayName: str
    fieldName: str
    filterTypeId: int
    filterLabelShortCode: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    dashboardCategory: DashboardCategoryDto


class PortfolioAndAccountsErrorDto(TypedDict, total=False):
    portfolioId: int
    portfolioName: str
    registrationId: int
    accountId: int
    externalAccountId: str
    symbol: str
    combinedErrorMessages: str
    errorSourceLevel: str
    errorType: str


class ImportLogDto(TypedDict, total=False):
    id: int
    firmId: int
    session: str
    type: int
    userId: int
    startExtractTime: str
    endExtractTime: str
    startImportTime: str
    endImportTime: str
    startAnalyticsTime: str
    endAnalyticsTime: str
    startTradeGenerationTime: str
    endTradeGenerationTime: str
    percentComplete: int
    status: int
    errorCount: int
    warningCount: int
    reason: str
    bucketName: str
    bucketPath: str
    correlationId: str
    rebalanceInstructions: list[RebalanceInstructions]
    editedDate: str
    requestedByIds: list[str]


class ImportLogHistoryItemDto(TypedDict, total=False):
    id: int
    session: str
    type: str
    userId: int
    startExtractTime: str
    endExtractTime: str
    startImportTime: str
    endImportTime: str
    startAnalyticsTime: str
    endAnalyticsTime: str
    startTradeGenerationTime: str
    endTradeGenerationTime: str
    percentComplete: int
    status: str
    errorCount: int
    warningCount: int
    reason: str
    bucketName: str
    bucketPath: str
    correlationId: str
    rebalanceInstructions: str
    editedDate: str
    totalExtractTime: float
    totalImportTime: float
    totalAnalyticsTime: float
    totalTradeGenerationTime: float
    analyticsStatus: str
    analyticsMessage: str


class ImportStatusInfoDto(TypedDict, total=False):
    type: str
    status: str
    correlationId: str
    avgImportDurationInSeconds: int


class RebalanceInstructions(TypedDict, total=False):
    alClient: int
    accountIds: list[int]
    regIds: list[int]


class ESGThemeRestrictionMinDto(TypedDict, total=False):
    id: int
    esgThemeId: int
    theme: str
    themeCode: str
    portfolioIds: list[int]
    isRestricted: bool


class EsgAssignmentDto(TypedDict, total=False):
    id: int
    theme: str
    themeCode: str
    cusip: str
    symbol: str


class EsgThemeDto(TypedDict, total=False):
    id: int
    theme: str
    themeCode: str


class UserDto(TypedDict, total=False):
    id: int
    orionConnectExternalId: int
    firstName: str
    lastName: str
    roleId: int
    isDeleted: bool
    path: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    email: str
    status: int
    tags: str
    startDate: str
    expireDate: str
    userLoginId: str
    notificationEmail: str
    requireSearch: bool
    theme: str


class UserGridViewDto(TypedDict, total=False):
    id: int
    viewName: str
    viewTypeId: int
    isDefault: bool
    isPublic: bool
    gridColumnDefs: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    tradeToolId: int


class UserGridViewRowCountDto(TypedDict, total=False):
    id: int
    viewName: str
    viewTypeId: int
    rowCount: int
    error: str


class UserGridViewSlimDto(TypedDict, total=False):
    id: int
    viewName: str
    viewTypeId: int
    isPublic: bool
    createdBy: int


class FixFieldDto(TypedDict, total=False):
    id: int
    name: str
    value: str
    description: str


class FixMessageDto(TypedDict, total=False):
    id: int
    blockOrderId: int
    msgType: str
    createdDate: str
    logText: str
    fields: list[FixFieldDto]


class Category(TypedDict, total=False):
    pendingInAmount: float
    pendingInPercent: float
    targetInAmount: float
    targetInPercent: float
    currentInAmount: float
    currentInPercent: float
    accountId: int
    aggregatedCurrentAmount: float
    aggregatedCurrentPercent: float
    aggregatedPostAmount: float
    aggregatedPostPercent: float
    effectiveTargetAmount: float
    effectiveTargetPercentage: float
    isMACSecurity: int
    isSMANode: int
    modelElementId: int
    modelId: int
    name: str
    nodeId: int
    parentModelDetailId: int
    portfolioId: int
    relatedType: str
    relatedTypeId: int
    securityName: str
    symbol: str
    inTolerance: bool
    assetClassType: str
    categoryId: int
    categoryName: str


class Class(TypedDict, total=False):
    pendingInAmount: float
    pendingInPercent: float
    targetInAmount: float
    targetInPercent: float
    currentInAmount: float
    currentInPercent: float
    accountId: int
    aggregatedCurrentAmount: float
    aggregatedCurrentPercent: float
    aggregatedPostAmount: float
    aggregatedPostPercent: float
    effectiveTargetAmount: float
    effectiveTargetPercentage: float
    isMACSecurity: int
    isSMANode: int
    modelElementId: int
    modelId: int
    name: str
    nodeId: int
    parentModelDetailId: int
    portfolioId: int
    relatedType: str
    relatedTypeId: int
    securityName: str
    symbol: str
    inTolerance: bool
    assetClassType: str
    classId: int
    className: str


class Detail(TypedDict, total=False):
    portfolioId: int
    needAnalytics: int
    failedReason: str
    totalAUM: float
    setAsideCash: float
    reserveCash: float
    reserveCashPercent: float
    setAsideCashPercent: float
    securities: list[AllocationDetails_Security]
    categories: list[Category]
    classes: list[Class]
    subClasses: list[SubClass]
    analyticsEditedDate: str


class AllocationDetails_Security(TypedDict, total=False):
    id: int
    isMACSecurity: int
    name: str
    pendingInAmount: float
    pendingInPercent: float
    securityId: int
    securitySetId: int
    securitySetName: str
    symbol: str
    targetInAmount: float
    targetInPercent: float
    currentInAmount: float
    currentInPercent: float
    parentModelDetailId: int
    smaLevel: str
    modelElementId: int
    isPortfolioSecurity: bool
    inTolerance: bool
    assetClassType: str


class SubClass(TypedDict, total=False):
    pendingInAmount: float
    pendingInPercent: float
    targetInAmount: float
    targetInPercent: float
    currentInAmount: float
    currentInPercent: float
    accountId: int
    aggregatedCurrentAmount: float
    aggregatedCurrentPercent: float
    aggregatedPostAmount: float
    aggregatedPostPercent: float
    effectiveTargetAmount: float
    effectiveTargetPercentage: float
    isMACSecurity: int
    isSMANode: int
    modelElementId: int
    modelId: int
    name: str
    nodeId: int
    parentModelDetailId: int
    portfolioId: int
    relatedType: str
    relatedTypeId: int
    securityName: str
    symbol: str
    inTolerance: bool
    assetClassType: str
    subClassId: int
    subClassName: str


class BatchJobDto(TypedDict, total=False):
    id: int
    type: str
    description: str
    startedDate: str
    completedDate: str
    status: str
    errorCount: int
    successCount: int
    totalCount: int
    percentComplete: int
    createdBy: str
    parameters: str
    correlationId: str
    details: list[BatchJobDetail]


class GlobalSearchDto(TypedDict, total=False):
    portfolios: list[SimpleSearchResultDto]
    accounts: list[SimpleSearchResultDto]
    models: list[SimpleSearchResultDto]


class SecurityPreferenceChangeParametersDto(TypedDict, total=False):
    runFor: str
    runForIds: list[int]
    lastRunMaxId: int
    primaryTeamId: int
    orionConnectFirmId: str


class BatchOptimizationStatusDto(TypedDict, total=False):
    batchName: str
    status: str
    comments: str
    isReady: bool


class BatchOptimizationSummaryDto(TypedDict, total=False):
    connectFirm: str
    accountId: str
    batchName: str
    externalBatchName: str
    accountName: str
    targetStrategy: str
    marketValue: float
    numberOfTrades: int
    turnOver: float
    optimalBeta: float
    optimalRSquared: float
    transactionCost: float
    proposedShortTermGainLoss: float
    proposedLongTermGainLoss: float
    taxCost: float
    ytdRealizedSTGain: float
    ytdRealizedLTGain: float
    currentTrackingError: float
    optimalTrackingError: float
    optimizationRun: str
    warning: str
    tradeInstanceId: int
    accountNumber: str
    currentCash: float
    currentCashPercent: float
    proposedCash: float
    proposedCashPercent: float
    cashDifference: float
    cashPercentDifference: float
    beginningNoOfSecurities: int
    endingNoOfSecurities: int
    proposedNetGainLoss: float
    ytdNetRealizedGainLoss: float
    taxCostPercent: float
    taxStatus: str
    accountType: str
    custodian: str
    regTradeBlocked: bool
    trackingErrorDifference: float
    firmName: str
    representativeName: str
    maxCapitalGains: float
    createdBy: str
    optimizationType: str
    optimizationStartTime: str
    previousDayTrackingError: float


class CommunitiesManagerDto(TypedDict, total=False):
    id: int
    name: str
    category: str
    abbreviation: str


class CommunitiesStrategistDto(TypedDict, total=False):
    id: int
    name: str
    abbreviation: str


class CommunitiesSyncObjectDto(TypedDict, total=False):
    strategist: CommunitiesStrategistDto
    manager: CommunitiesManagerDto
    model: CommunityModelDto


class CommunityModelDto(TypedDict, total=False):
    modelId: int
    modelName: str
    managementStyle: str
    action: str
    requiresRebalance: bool
    targetRiskUpper: float
    targetRiskLower: float
    style: str
    advisorFee: float
    weightedAvgNetExpenses: float
    currentRisk: float
    minimumAmount: float
    strategistId: int
    modelManagerId: int
    astroUsage: int
    isSMA: bool
    optionLevelApproval: str
    securities: list[CommunityModelItemDto]
    skipStatusUpdate: bool
    astroTemplateId: str
    altsManagedByStrategist: bool
    altsModelLevel: bool
    allowAlternativeToleranceBands: bool


class CommunityModelItemDto(TypedDict, total=False):
    ticker: str
    targetPercent: float
    upperTolerance: float
    lowerTolerance: float
    assetCategoryName: str
    assetClassName: str
    subClassName: str
    tlhSecurities: list[TlhSecurity]


class TlhSecurity(TypedDict, total=False):
    productId: int


class HiddenLeversFixedIncomeMatruityBreakdownDto(TypedDict, total=False):
    intermediate: float
    long: float
    lessthan1Year: float
    short: float


class HiddenLeversFixedIncomeSectorBreakdownDto(TypedDict, total=False):
    government: float
    cashEquivalent: float
    corporate: float
    securitized: float
    other: float
    municipal: float


class HiddenLeversRiskProfileDto(TypedDict, total=False):
    currentRisk: int
    riskAndReturnOver: str
    upsidePct: float
    upsideAmt: float
    downsidePct: float
    downsideAmt: float
    sharpeRatio: float
    maxDrawdown: float
    sortinoRatio: float
    # yield: float  # non-identifier key
    correlationRisk: float
    styleRawBreakdown: HiddenLeversStyleRawBreakdownDto
    fiMaturityBreakdown: HiddenLeversFixedIncomeMatruityBreakdownDto
    fiSectorBreakdown: HiddenLeversFixedIncomeSectorBreakdownDto


class HiddenLeversStressTestResultDto(TypedDict, total=False):
    timeframe: str
    name: str
    id: int
    totalImpact: float
    outcome: str


class HiddenLeversStyleRawBreakdownDto(TypedDict, total=False):
    largeBlend: float
    midBlend: float
    smallBlend: float
    largeValue: float
    midValue: float
    smallValue: float
    largeGrowth: float
    midGrowth: float
    smallGrowth: float


class HiddenLeversUserStatusDto(TypedDict, total=False):
    isPaidUser: bool


class LogEnvelope(TypedDict, total=False):
    system: str
    subsystem: str
    logLevel: str
    logCode: int
    message: Any


class SmaAccountTypeRestrictionLookupDto(TypedDict, total=False):
    id: int
    name: str
    category: str
    value: str


class AccountSectorIndustryRestrictionsDto(TypedDict, total=False):
    connectAccountId: str
    sectors: list[SectorDto]


class IndustryDto(TypedDict, total=False):
    id: str
    name: str
    penalty: float
    minimumValue: float
    maximumValue: float
    sectorId: str


class SectorDto(TypedDict, total=False):
    id: str
    name: str
    penalty: str
    minimumValue: float
    maximumValue: float
    industries: list[IndustryDto]


class CreateMcpServerDto(TypedDict, total=False):
    name: str
    url: str
    description: str
    instructions: str
    headers: dict[str, Any]
    useEclipseSession: bool


class McpServerDto(TypedDict, total=False):
    id: int
    name: str
    url: str
    description: str
    instructions: str
    headers: dict[str, Any]
    useEclipseSession: bool
    createdDate: str
    createdBy: int
    createdByName: str
    editedDate: str
    editedBy: int
    editedByName: str


class UpdateMcpServerDto(TypedDict, total=False):
    id: int
    name: str
    url: str
    description: str
    instructions: str
    headers: dict[str, Any]
    useEclipseSession: bool


class DetailedModelInfoBasedOnUserAccessibilityDto(TypedDict, total=False):
    id: int
    name: str
    sleeveCount: int
    portfolioCount: int
    source: str
    hasSubstitute: bool
    statusId: int
    status: str
    nameSpace: str
    currentStatusId: int
    tags: str
    isDynamic: bool
    isSubstitutedForPortfolio: bool
    description: str
    ownerUserId: int
    ownerUser: str
    managementStyleId: int
    managementStyle: str
    isCommunityModel: bool
    communityModelId: int
    lastSyncDate: str
    approvedByUserId: int
    approvedByUser: str
    isDeleted: bool
    createdOn: str
    editedOn: str
    teamId: int
    modelTeamIds: str
    teamName: str
    teamNames: str
    createdBy: str
    editedBy: str
    hasEditAccess: bool
    isMAC: bool
    needsUpdate: bool
    updateStatus: str
    isSMA: bool
    isOptionTradingAllowed: bool
    astroTemplateId: str
    modelAUM: float
    sleeveSuffix: str
    excludeRebalanceSleeve: bool
    modelTypeName: str
    lastRebalanced: str
    dateRebalanceRequested: str
    needsRebalance: bool


class ExpiredAccountSetAsidesAndTransactions(TypedDict, total=False):
    setAsides: list[ExpiredAccountSetAside]
    transactions: list[TransactionsForSetAsides]


class GetAssignedModelsRequest(TypedDict, total=False):
    type: str
    ids: list[int]


class GetHLStressTestResultRequest(TypedDict, total=False):
    modelId: int
    scenarioIds: list[int]


class ModelAnalysis(TypedDict, total=False):
    levelsData: list[LevelData]
    portfolioFlag: list[PortfolioFlag]


class ModelDetailDto(TypedDict, total=False):
    id: int
    modelId: int
    modelElementId: int
    leftValue: int
    rightValue: int
    rank: int
    level: str
    isSubstituted: bool
    substituteOf: int
    targetPercent: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    toleranceType: int
    toleranceTypeValue: float
    lowerModelToleranceAmount: float
    upperModelToleranceAmount: float
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    modelElement: ModelElementDto


class ModelDto(TypedDict, total=False):
    id: int
    name: str
    displayName: str
    namespace: str
    statusId: int
    description: str
    dynamicModel: bool
    scope: str
    tags: str
    managementStyleId: int
    ownerUserId: int
    approvedBy: int
    isSubModel: bool
    isCommunityModel: bool
    communityModelId: int
    isSubstitutedForPortfolio: bool
    isSubstitutedForSleeve: bool
    substituteOfModelId: int
    isDeleted: bool
    changeSource: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    astroEnabled: bool
    astroTemplateId: str
    astroUsage: int
    isSMA: bool
    sleeveSuffix: str
    modelTypeId: int
    details: list[ModelDetailDto]


class ModelElementDto(TypedDict, total=False):
    id: int
    name: str
    relatedType: str
    relatedTypeId: int
    isFavorite: bool
    namespace: str
    forCopy: bool
    validateTickerSet: bool
    rebalancePriority: int
    tags: str
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    securitySet: SecuritySetDto


class ModelLevel(TypedDict, total=False):
    id: str
    name: str
    displayName: str


class ModelProductClassSimpleDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    category: str
    categoryAbbreviation: str


class ModelRiskCategoriesSimpleDto(TypedDict, total=False):
    id: int
    abbreviation: str
    fullName: str


class ModelSyncToOCFirmDto(TypedDict, total=False):
    orionConnectFirmId: int
    orionConnectFirmName: str
    isSelected: bool


class ModelTypeDto(TypedDict, total=False):
    id: int
    name: str


class OCModelAggSyncRequestDto(TypedDict, total=False):
    modelAggs: list[OcModelAggSyncDto]


class OcModelAggSyncDto(TypedDict, total=False):
    modelAggId: int
    modelAggName: str
    modelAggType: str
    astroTemplate: str
    tags: str
    accountNumberSuffix: str
    models: list[OcModelSyncDto]


class OcModelItemSyncDto(TypedDict, total=False):
    productId: int
    ticker: str
    targetAllocation: float
    itemTolerance: int
    upperTolerance: float
    lowerTolerance: float


class OcModelSyncDto(TypedDict, total=False):
    id: int
    name: str
    isDynamic: bool
    weight: float
    modelItems: list[OcModelItemSyncDto]


class SimpleAstroModelDto(TypedDict, total=False):
    id: int
    name: str
    astroTemplateId: str


class TickerBasedModelDto(TypedDict, total=False):
    name: str
    description: str
    toleranceType: int
    toleranceTypeValue: float
    securities: list[TickerBasedModelSecuritySetItemDto]
    securitySetTlh: list[TickerBasedModelTlhInSecuritySet]


class UnexpiredSetAsidesWithTransactions(TypedDict, total=False):
    setAsides: list[UnexpiredAccountSetAside]
    transactions: list[TransactionsForSetAsides]


class NoteDto(TypedDict, total=False):
    id: int
    relatedType: int
    relatedId: int
    entityName: str
    notes: str
    startDate: str
    endDate: str
    displayNote: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    reviewedBy: int
    reviewDate: str
    createdByUser: str
    editedByUser: str
    orionConnectNote: bool
    isDeleted: bool


class NoteHistoryDto(TypedDict, total=False):
    id: int
    relatedType: int
    relatedId: int
    entityName: str
    notes: str
    startDate: str
    endDate: str
    displayNote: str
    createdDate: str
    editedDate: str
    reviewedBy: int
    reviewDate: str
    createdByUser: str
    editedByUser: str
    orionConnectNote: str
    isDeleted: bool
    changeType: str


class OptimizationBatchDetailDto(TypedDict, total=False):
    holdings: list[OptimizationHoldingDto]
    lots: list[OptimizationLotDto]
    accountInternalId: int
    accountId: str
    accountNumber: str
    accountName: str
    portfolioId: int
    portfolioName: str
    targetStrategyName: str
    exposureModel: str
    investmentStrategyTemplate: str
    batchId: str
    totalMarketValue: float
    managedValue: float
    startingSecurityCount: int
    endingSecurityCount: int
    turnoverPercent: float
    endingCashAmount: float
    endingCashPercent: float
    initialTrackingError: float
    optimalTrackingError: float
    optimizationNetGain: float
    optimizationShortTermGain: float
    optimizationLongTermGain: float
    ytdNetGain: float
    ytdShortTermGain: float
    ytdLongTermGain: float
    warning: str
    generatedSummary: str


class OptimizationHoldingDto(TypedDict, total=False):
    securityId: str
    ticker: str
    marketValue: float
    securityName: str
    costBasis: float
    acquiredDate: str
    initialShares: float
    finalShares: float
    changeShares: float
    initialPercentOfPortfolio: float
    finalPercentOfPortfolio: float
    targetPercent: float
    activeExposurePercent: float
    transactionValue: float
    tax: float
    realizedGainLoss: float


class OptimizationLotDto(TypedDict, total=False):
    id: int
    optimizationSummaryId: int
    ocProductId: int
    ticker: str
    securityName: str
    initShares: float
    optShares: float
    changeShares: float
    initPercent: float
    optPercent: float
    targetPercent: float
    activeWeight: float
    changeValue: float
    marketValue: float
    marketPrice: float
    unrealizedGainLoss: float
    unrealizedGainLossType: str
    proposedGainLoss: float
    proposedGainLossType: str
    buyDate: str
    buyPrice: float
    costBasis: float
    restrictionType: str
    restrictionSource: str


class OptimizationMessagesDto(TypedDict, total=False):
    batchId: str
    accountId: str
    warning: str


class OptimizationSummaryDto(TypedDict, total=False):
    id: int
    correlationId: str
    batchId: str
    accountInternalId: int
    accountId: str
    accountNumber: str
    accountName: str
    accountType: str
    custodian: str
    representativeName: str
    firmName: str
    asOfDate: str
    status: str
    optimizationStartTime: str
    optimizationType: int
    currentTrackingError: float
    marketValue: float
    optimalBeta: float
    optimalRSquared: float
    optimalTrackingError: float
    proposedLongTermGainLoss: float
    proposedShortTermGainLoss: float
    taxCost: float
    tradeInstanceId: int
    trades: int
    transactionCost: float
    turnOver: float
    hasWarning: bool
    hasGeneratedSummary: bool
    ytdRealizedShortTermGain: float
    ytdRealizedLongTermGain: float
    currentCash: float
    currentCashPercent: float
    proposedCash: float
    proposedCashPercent: float
    cashDifference: float
    cashPercentDifference: float
    beginningNoOfSecurities: int
    endingNoOfSecurities: int
    proposedNetGainLoss: float
    taxCostPercent: float
    ytdNetRealizedGainLoss: float
    taxStatus: str
    trackingErrorDifference: float
    maxCapitalGains: float
    createdBy: str


class PlaceOptimizationTradesRequest(TypedDict, total=False):
    summaryIds: list[int]


class PlaceOptimizationTradesResponse(TypedDict, total=False):
    correlationId: str


class InitialOptionAccountInfoRequest(TypedDict, total=False):
    ids: list[int]


class PortfolioAccountDto(TypedDict, total=False):
    accountId: str
    accountNumber: str
    accountType: str
    cashNeedAmount: float
    cashNeedPercentage: float
    contribution: float
    createdBy: str
    createdOn: str
    currentCash: float
    currentCashPercent: float
    custodianName: str
    distributionAmt: float
    doNotTrade: str
    editedBy: str
    editedOn: str
    excludedValue: float
    id: int
    isDisabled: int
    isSma: int
    managedValue: float
    managementStyle: str
    style: str
    model: str
    modelId: int
    name: str
    needAnalytics: int
    ocFirmId: int
    pendingCashPercent: float
    pendingCashValue: float
    pendingValue: float
    pendingValuePercent: float
    portfolioGroupId: int
    reserveCashActual: float
    reserveCashTarget: float
    setAsideCashActual: float
    setAsideCashTarget: float
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    sleeveTarget: float
    sleeveToleranceLower: float
    sleeveToleranceUpper: float
    sleeveType: str
    status: str
    statusInfo: str
    targetCash: float
    targetCashPercent: float
    taxQualification: str
    totalValue: float
    tradesPending: int
    excludeRebalanceSleeve: str
    hasOptionsExpiringSoon: bool
    householdId: int
    subAdvisorName: str
    lastRebalancedOn: str
    lastTradedDate: str
    representativeNumber: str
    householdName: str
    accountTags: str
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedTotalGain: float
    outsideId: str
    secondaryAccountNumber: str
    sleeveCurrentPercent: float
    sleeveNeedPercent: float
    sleeveTargetPercent: float
    systematicAmount: float
    systematicDate: str
    notesCount: int
    displayNotes: str
    teamNotes: str
    postTradeNeedPercent: float
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    modelTags: str
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float
    modelDeviationPercent: float
    lastTLHDate: str
    sweepCash: float
    sweepCashPercent: float
    moneyMarketCash: float
    moneyMarketCashPercent: float
    orionConnectExternalId: int
    autoRebalanceType: str
    nextAutoRebalanceDate: str
    representativeId: str
    maxSetAsideCash: float
    minSetAsideCash: float
    tradingBlocksCount: int
    tradingBlocks: str
    accountStatus: str
    managed: str
    orionConnectFirmName: str
    astroEnabled: int
    managedCashValue: float
    managedCashPercent: float
    rmdAmount: float
    rmdRemaining: float
    distributionAmtYTD: float
    sleeveContributionMethod: str
    sleeveDistributionMethod: str
    accountCashTolerance: str


class PortfolioAutoRebalanceHistoryDto(TypedDict, total=False):
    changeType: str
    autoRebalance: str
    autoRebalanceDay: int
    autoRebalanceMonth: str
    editedDate: str
    editedBy: str
    createdDate: str
    createdBy: str


class PortfolioCashDetailsDto(TypedDict, total=False):
    distributionAmount: float
    contributionAmount: float
    currentCashAmount: float
    currentCashPercent: float
    availableCash: float
    managedCashValue: float
    managedCashPercent: float
    targetCashAmount: float
    targetCashPercent: float
    managedValue: float
    setAsideCashTarget: float
    setAsideCashTargetPercent: float
    setAsideCashActual: float
    setAsideCashActualPercent: float
    setAsideMinAmount: float
    setAsideMinPercent: float
    setAsideMaxAmount: float
    setAsideMaxPercent: float


class AUM(TypedDict, total=False):
    total: float
    totalValue: float
    managedValue: float
    excludedValue: float
    totalCash: AUMTotalCash


class AUMTotalCash(TypedDict, total=False):
    total: float
    reserve: float
    cash: float
    setAsideCash: float
    reserveCashPercent: float
    setAsideCashPercent: float


class General(TypedDict, total=False):
    portfolioName: str
    macStatus: int
    sleevePortfolio: int
    custodialAccountNumber: str
    registrationId: int
    sleeveStrategy: str
    contributionMethod: str
    distributionMethod: str
    substitutedModelId: int
    modelId: int
    modelName: str
    autoRebalance: str
    monthAndDate: str
    rebalanceTypeId: int
    rebalanceType: str
    rebalanceOptionId: int
    rebalanceOption: str
    rebalanceDay: int
    lastRebalanceDate: str
    doNotTrade: bool
    tradingInstruction: str
    sellEmphasisOn: int
    buyEmphasisOn: int
    tags: str
    fixedIncomeTradeBlockDate: str
    pendingApprovalModelId: int
    pendingApprovalModelName: str
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    lastTradedDate: str
    lastTLHDate: str
    sleeveDeviationPercent: float
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float


class Issues(TypedDict, total=False):
    outOfTolerance: int
    cashNeed: float
    setForAutoRebalance: int
    contributions: float
    distribution: float
    modelAssociation: int
    doNotTrade: int
    tlhOpportunity: int
    dataErrors: int
    pendingTrades: int


class PortfolioDetails(TypedDict, total=False):
    id: int
    needAnalytics: int
    needAnalyticsStatus: str
    needAnalyticsToTradeStatus: str
    failedReason: str
    isDeleted: int
    isDisabled: int
    createdBy: str
    createdOn: str
    editedBy: str
    editedOn: str
    analyticsEditedDate: str
    general: General
    issues: Issues
    teams: list[TeamDto]
    summary: PortfolioDetails_Summary
    disabledReason: str
    orionConnectFirmId: int
    portfolioGroupId: int


class PortfolioSummaryDto(TypedDict, total=False):
    id: int
    name: str
    tags: str
    isSleevePortfolio: bool
    doNotTrade: bool
    registrationId: int
    totalValue: float
    managedValue: float
    excludedValue: float
    modelId: int
    modelName: str
    custodialAccountNumber: str
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    sleeveDeviationPercent: float
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float
    autoRebalance: str
    outOfTolerance: bool
    cashOutOfTolerance: bool
    cashNeed: float
    contribution: float
    distribution: float
    cashNeedPercentage: float
    cashTargetPercent: float
    cashPercent: float
    cashValue: float
    actualSetAsideCash: float
    targetSetAsideCash: float
    hasUnassignedHoldings: bool
    hasSubstitutes: bool
    hasTLHOpportunity: bool
    hasPendingTrades: bool
    underMaxGainAmount: bool
    analyticsEditedDate: str
    lastTLHDate: str
    lastTradedDate: str
    lastRebalanceDate: str
    needAnalytics: int
    needAnalyticsStatus: str
    failedReason: str
    isDisabled: int
    sellEmphasisOn: int
    buyEmphasisOn: int
    rebalanceDay: int
    rebalanceTypeId: int
    rebalanceOption: str
    rebalanceType: str
    rebalanceOptionId: int
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    orionConnectFirmId: int
    portfolioGroupId: int
    teams: list[TeamDto]
    nextAutoRebalanceDate: str
    pendingApprovalModelId: int
    pendingApprovalModelName: str
    pendingApprovalModelDescription: str
    macStatus: int
    substitutedModelId: int
    modelDescription: str
    minSetAsideCash: float
    maxSetAsideCash: float


class Realized(TypedDict, total=False):
    total: float
    totalStatus: str
    shortTerm: float
    shortTermStatus: str
    longTerm: float
    longTermStatus: str


class PortfolioDetails_Summary(TypedDict, total=False):
    analyticsOn: str
    reserveCashTarget: float
    reserveCashActual: float
    targetCash: float
    currentCash: float
    pendingCash: float
    aum: AUM
    realized: Realized


class TeamDto(TypedDict, total=False):
    id: int
    name: str
    isPrimary: int
    portfolioAccess: int


class PortfolioDto(TypedDict, total=False):
    id: int
    name: str
    portfolioGroupId: int
    portfolioGroupName: str
    description: str
    modelId: int
    substitutedModelId: int
    tags: str
    isDisabled: bool
    disabledReason: str
    isSleevePortfolio: bool
    sleeveContributionMethod: str
    sleeveDistributionMethod: str
    sleeveStrategyName: str
    registrationId: int
    doNotTrade: bool
    tradingInstruction: str
    sellEmphasisOn: int
    buyEmphasisOn: int
    householdId: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    orionConnectFirmId: int


class PortfolioDynamicListDto(TypedDict, total=False):
    id: int
    name: str
    modelName: str
    modelId: str
    portfolioGroupId: int
    isSleevePortfolio: int
    primaryTeam: str
    teamNames: str
    managedValue: float
    excludedValue: float
    totalValue: float
    tradesPending: float
    deviationPercent: float
    cashNeedPercentage: float
    cashNeedAmount: float
    tradingInstruction: str
    taxQualification: str
    numOfAssociatedAccounts: int
    distributionAmt: float
    reserveCashTarget: float
    reserveCashActual: float
    setAsideCashTarget: float
    setAsideCashActual: float
    targetCash: float
    targetCashPercent: float
    currentCash: float
    currentCashPercent: float
    pendingCash: float
    pendingCashPercent: float
    cashOverage: float
    cashOveragePercent: float
    cashUnderage: float
    cashUnderagePercent: float
    pendingValue: float
    pendingValuePercent: float
    autoRebalanceOn: int
    contribution: float
    tradeBlocked: int
    status: str
    statusReason: str
    hasTaxLossHarvest: int
    style: str
    lastRebalancedDate: str
    lastTradedDate: str
    isDisabled: bool
    nextAutoRebalanceDate: str
    isDeleted: bool
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    needAnalyticsStatus: str
    needAnalyticsToTradeStatus: str
    needAnalyticsFailedReason: str
    isMac: int
    fixedIncomeTradeBlockDate: str
    tags: str
    cashOutOfTolerance: str
    portfolioOutOfTolerance: str
    hasUnassignedHoldings: str
    excludeOOT: str
    excludeOOTDate: str
    excludeCashNeeds: str
    excludeCashNeedsDate: str
    excludeTLH: str
    excludeTLHDate: str
    isOptionTradingAllowed: bool
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    accountId: str
    accountNumber: str
    accountType: str
    custodianName: str
    hasOptionsExpiringSoon: bool
    householdId: str
    subAdvisorName: str
    outputColumns: list[str]
    registrationId: int
    hasSubstitute: int
    managementStyle: str
    representativeNames: str
    representativeNumber: str
    householdName: str
    accountTags: str
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedTotalGain: float
    outsideId: str
    secondaryAccountNumber: str
    autoRebalanceType: str
    orionConnectFirmId: int
    maxGainAmountDollar: float
    maxGainAmountPercent: float
    notesCount: int
    displayNotes: str
    teamNotes: str
    systematicAmount: float
    systematicDate: str
    netCapitalGain: float
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    carryForwardLossAmount: float
    sleeveDeviationPercent: float
    securityDeviationPercent: float
    securitySetDeviationPercent: float
    modelDeviationPercent: float
    modelTags: str
    maxShortTermGainDollar: float
    maxShortTermGainPercent: float
    subclassDeviationPercent: float
    classDeviationPercent: float
    categoryDeviationPercent: float
    lastTLHDate: str
    sweepCash: float
    sweepCashPercent: float
    moneyMarketCash: float
    moneyMarketCashPercent: float
    representativeId: str
    maxSetAsideCash: float
    minSetAsideCash: float
    tradingBlocksCount: int
    tradingBlocks: str
    accountStatus: str
    managed: str
    orionConnectFirmName: str
    managedCashValue: float
    managedCashPercent: float
    rmdAmount: float
    rmdRemaining: float
    distributionAmtYTD: float
    sleeveContributionMethod: str
    sleeveDistributionMethod: str
    accountCashTolerance: str
    macStatus: str


class PortfolioExternalAccountIdRequest(TypedDict, total=False):
    accountId: int
    alClientId: int


class PortfolioGainLossSummaryDto(TypedDict, total=False):
    portfolioId: int
    underMaxGainAmount: bool
    carryForwardLossAmount: float
    maxGainAmountDollar: float
    maxGainAmountPercent: float
    maxShortTermGainDollar: float
    maxShortTermGainPercent: float
    netCapitalGain: float
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    ytdRealizedTotalGain: float
    unRealizedLongTermGain: float
    unRealizedShortTermGain: float
    unRealizedTotalGain: float


class PortfolioListDto(TypedDict, total=False):
    id: int
    name: str
    portfolioGroupId: int
    model: str
    modelId: str
    sleevePortfolio: int
    team: str
    teamNames: str
    managedValue: float
    excludedValue: float
    totalValue: float
    tradesPending: float
    percentDeviations: float
    cashNeedPercentage: float
    cashNeedAmount: float
    tradingInstruction: str
    taxQualification: str
    numOfAssociatedAccounts: int
    distributionAmt: float
    reserveCashTarget: float
    reserveCashActual: float
    setAsideCashTarget: float
    setAsideCashActual: float
    targetCash: float
    targetCashPercent: float
    currentCash: float
    currentCashPercent: float
    pendingCash: float
    pendingCashPercent: float
    cashOverage: float
    cashOveragePercent: float
    cashUnderage: float
    cashUnderagePercent: float
    pendingValue: float
    pendingValuePercent: float
    autoRebalanceOn: int
    contribution: float
    tradeBlocked: int
    status: str
    statusInfo: str
    tlh: int
    style: str
    lastRebalancedOn: str
    isDisabled: bool
    nextAutoRebalanceDate: str
    isDeleted: bool
    createdOn: str
    createdBy: str
    editedOn: str
    editedBy: str
    needAnalyticsStatus: str
    needAnalyticsToTradeStatus: str
    portfolioDisabledReason: str
    needAnalyticsFailedReason: str
    isMac: int
    fixedIncomeTradeBlockDate: str
    tags: str
    cashOutOfTolerance: str
    portfolioOutOfTolerance: str
    hasUnassignedHoldings: str
    excludeOOT: str
    excludeOOTDate: str
    excludeCashNeeds: str
    excludeCashNeedsDate: str
    excludeTLH: str
    excludeTLHDate: str
    isOptionTradingAllowed: bool
    sleeveStrategyAggregateId: str
    sleeveStrategyAggregateName: str
    accountId: str
    accountNumber: str
    accountType: str
    custodianName: str
    hasOptionsExpiringSoon: bool
    householdId: str
    subAdvisorName: str
    lastTradedDate: str
    registrationId: int
    representativeNames: str
    managementStyle: str
    hasSubstitute: int
    representativeNumber: str
    householdName: str
    accountTags: str
    ytdRealizedLongTermGain: float
    ytdRealizedShortTermGain: float
    outsideId: str
    secondaryAccountNumber: str
    autoRebalanceType: str
    maxGainAmountDollar: float
    maxGainAmountPercent: float
    ytdRealizedTotalGain: float
    systematicAmount: float
    systematicDate: str
    notesCount: int
    displayNotes: str
    netCapitalGain: float
    teamNotes: str
    maxShortTermGainDollar: float
    maxShortTermGainPercent: float


class PortfolioMacHistoryDto(TypedDict, total=False):
    statuses: list[MacStatus]
    details: list[MacDetail]


class PortfolioSubstitutionsHistoryDto(TypedDict, total=False):
    substituteFrom: str
    substituteTo: str
    editedDate: str
    editedBy: str
    changeType: str


class PortfolioTeamHistoryDto(TypedDict, total=False):
    name: str
    action: str
    primary: int
    editedDate: str
    editedBy: str


class PortfolioTreeDto(TypedDict, total=False):
    id: int
    name: str
    value: float
    accounts: list[AccountSimpleDto]


class MoneyMarketAllocationAuditHistoryDto(TypedDict, total=False):
    moneyMarketCashValueFrom: float
    moneyMarketCashValueTo: float
    moneyMarketTargetValue: float
    moneyMarketMinValue: float
    moneyMarketMaxValue: float
    recordId: int
    recordName: str
    changeType: str
    level: str
    editedOn: str
    editedBy: str


class MoneyMarketAllocationDto(TypedDict, total=False):
    id: int
    moneyMarketCashValueFrom: float
    moneyMarketCashValueTo: float
    moneyMarketTargetValue: float
    moneyMarketMinValue: float
    moneyMarketMaxValue: float
    relatedType: int
    relatedTypeId: int


class MoneyMarketAllocationPreferenceDto(TypedDict, total=False):
    id: int
    recordId: int
    relatedType: int
    preferenceId: int
    preferenceName: str
    displayName: str
    componentName: str
    componentType: str
    categoryType: str
    moneyMarketAllocations: list[MoneyMarketAllocationDto]
    inheritedMoneyMarketAllocations: list[MoneyMarketAllocationDto]


class MoneyMarketAllocationPreferenceSaveDto(TypedDict, total=False):
    preferenceValueId: int
    relatedTypeId: int
    relatedType: int
    preferenceId: int
    relatedTypeIds: list[int]
    moneyMarketAllocations: list[MoneyMarketAllocationDto]
    resetToParent: bool


class MoneyMarketFundAuditHistoryDto(TypedDict, total=False):
    securityId: int
    securityName: str
    symbol: str
    moneyMarketMinInitialInvestment: float
    recordId: int
    recordName: str
    changeType: str
    level: str
    editedOn: str
    editedBy: str


class MoneyMarketFundDto(TypedDict, total=False):
    securityId: int
    securityName: str
    symbol: str
    moneyMarketMinInitialInvestment: float
    relatedType: int
    relatedTypeId: int


class MoneyMarketFundPreferenceDto(TypedDict, total=False):
    id: int
    recordId: int
    relatedType: int
    preferenceId: int
    preferenceName: str
    displayName: str
    componentName: str
    componentType: str
    categoryType: str
    moneyMarketFunds: list[MoneyMarketFundDto]
    inheritedMoneyMarketFunds: list[MoneyMarketFundDto]


class MoneyMarketFundPreferenceSaveDto(TypedDict, total=False):
    preferenceValueId: int
    relatedTypeId: int
    relatedType: int
    preferenceId: int
    relatedTypeIds: list[int]
    moneyMarketFunds: list[MoneyMarketFundDto]
    resetToParent: bool


class MoneyMarketPreferenceAuditHistoryDto(TypedDict, total=False):
    marketMarketAllocationAuditHistories: list[MoneyMarketAllocationAuditHistoryDto]
    marketMarketFundAuditHistories: list[MoneyMarketFundAuditHistoryDto]


class SecurityMoneyMarketFundPreferenceDto(TypedDict, total=False):
    securityId: int
    securityName: str
    symbol: str
    moneyMarketMinInitialInvestment: float
    relatedType: int
    relatedTypeId: int
    relatedTypeName: str


class UserGridRankedViewDto(TypedDict, total=False):
    id: int
    userId: int
    viewId: int
    viewName: str
    typeName: str
    viewTypeId: int
    rank: int
    isDefault: bool
    canEdit: bool
    isPublic: bool
    gridColumnDefs: str
    tradeToolId: int


class QueryColumnStateDto(TypedDict, total=False):
    colId: str
    sort: str
    sortOrder: int
    filters: list[QueryColumnStateFilterDto]


class QueryColumnStateFilterDto(TypedDict, total=False):
    dataType: str
    comparator: str
    values: list[str]


class QueryStateDto(TypedDict, total=False):
    matchAll: bool
    columns: list[QueryColumnStateDto]


class SimpleSearchResultDto(TypedDict, total=False):
    id: int
    name: str
    value: float
    isDeleted: bool


class SecurityDto(TypedDict, total=False):
    id: int
    orionFirmId: int
    orionConnectExternalId: int
    symbol: str
    name: str
    orionEclipseName: str
    assetCategoryId: int
    assetClassId: int
    assetSubClassId: int
    securityType: int
    status: int
    isDeleted: bool
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isCustodialCash: bool
    orionEclipseFirmId: int
    isSystemGenerated: bool
    cusip: str
    maintainInEclipse: bool
    isMultiAssetClass: int
    price: float


class SecurityModelDto(TypedDict, total=False):
    modelId: int
    relatedType: int
    securityId: int
    securitySetId: int
    securityType: str


class SecurityPriceChangeDto(TypedDict, total=False):
    id: int
    ticker: str
    currentPrice: float
    sourceChangeEventDate: str
    sourceIdentifier: str
    custodianId: int
    custodialName: str
    changeStatusId: int
    changeStatus: str
    createdDate: str
    processedDate: str
    processedBy: int


class SecurityPriceDto(TypedDict, total=False):
    id: int
    securityId: int
    price: float
    priceType: str
    priceDateTime: str
    isDeleted: int
    createddate: str
    createdBy: int
    editeddate: str
    updatedBy: str
    editedBy: int
    symbol: str


class SecurityEquivalenceInSecuritySetHistoryDto(TypedDict, total=False):
    securitySetId: int
    securityId: int
    symbol: str
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    changeType: str
    equivalentSecurityId: int
    equivalentSymbol: str
    equivalentName: str
    buyPriority: str
    sellPriority: str
    doNotTlh: str


class SecurityGroupEquivalenceInSecuritySetHistoryDto(TypedDict, total=False):
    securitySetId: int
    securityId: int
    symbol: str
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    changeType: str
    equivalentType: int
    equivalentTypeName: str
    equivalentTypeId: int
    equivalentTypeIdName: str
    buyPriority: str
    sellPriority: str


class SecuritySetAlternativeHistoryDto(TypedDict, total=False):
    securitySetId: int
    securityId: int
    symbol: str
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    changeType: str
    custodianId: int
    custodian: str
    equivalentSecurityId: int
    equivalentSymbol: str
    taxableSecurityId: int
    taxableSymbol: str
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredSecurityId: int
    taxDeferredSymbol: str
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptSecurityId: int
    taxExemptSymbol: str
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float


class SecuritySetDetailHistoryDto(TypedDict, total=False):
    securitySetId: int
    securityId: int
    symbol: str
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    changeType: str
    securityName: str
    rank: int
    targetPercent: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: str
    sellPriority: str
    doNotTlh: str


class SecuritySetDetailHistoryResponseDto(TypedDict, total=False):
    details: list[SecuritySetDetailHistoryDto]
    tlhSecurities: list[SecurityTLHInSecuritySetHistoryDto]
    groupEquivalences: list[SecurityGroupEquivalenceInSecuritySetHistoryDto]
    equivalences: list[SecurityEquivalenceInSecuritySetHistoryDto]
    alternatives: list[SecuritySetAlternativeHistoryDto]


class SecuritySetDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    isDynamic: bool
    isDeleted: int
    isCommunityModel: bool
    overrideStrategistUpdates: bool
    isModelAssigned: int
    toleranceType: int
    toleranceTypeValue: float
    createdOn: str
    createdBy: int
    editedBy: int
    editedOn: str
    access: int
    canEdit: bool
    isOwner: bool


class SecuritySetHistoryDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    isDynamic: str
    toleranceType: str
    toleranceTypeValue: float
    doNotTlh: str
    benchmarkAsset: str
    isCommunityModel: str
    alternativesManagedByStrategist: str
    overrideStrategistUpdates: str
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    changeType: str


class SecurityTLHInSecuritySetHistoryDto(TypedDict, total=False):
    securitySetId: int
    securityId: int
    symbol: str
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    changeType: str
    custodianId: int
    custodian: str
    tlhSecurityId: int
    tlhSymbol: str
    tlhSecurity: str
    priority: int


class SpSecuritySetDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    isDynamic: bool
    isDeleted: bool
    isCommunityModel: bool
    isModelAssigned: bool
    toleranceType: str
    toleranceTypeValue: float
    createdOn: str
    createdBy: str
    editedBy: str
    editedOn: str
    access: int
    canEdit: bool
    isOwner: bool
    isFavorite: bool
    tlhAltsManagedBy: str
    overrideToleranceBands: bool
    containsEquivalent: bool


class TickerBasedModelAlternativeDto(TypedDict, total=False):
    ticker: str
    custodian: str
    equivalentSecurityTicker: str
    relatedType: int
    relatedTypeId: int
    taxableSecurityTicker: str
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredSecurityTicker: str
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptSecurityTicker: str
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float


class TickerBasedModelEquivalentDto(TypedDict, total=False):
    ticker: str
    equivalentSecurityTicker: str
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    rank: int
    doNotTlh: bool


class TickerBasedModelSecuritySetItemDto(TypedDict, total=False):
    ticker: str
    targetPercent: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    lowerModelToleranceAmount: float
    upperModelToleranceAmount: float
    rank: int
    minimumTradeAmount: float
    minimumInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    groupEquivalentType: int
    groupEquivalent: int
    groupEquivalentBuyPriority: int
    groupEquivalentSellPriority: int
    doNotTlh: bool
    equivalents: list[TickerBasedModelEquivalentDto]
    alternatives: list[TickerBasedModelAlternativeDto]
    tlhSecurities: list[TickerBasedModelTlhSecurityDto]


class TickerBasedModelTlhInSecuritySet(TypedDict, total=False):
    ticker: str
    custodian: str
    tlhSecurityTicker: str
    priority: int


class TickerBasedModelTlhSecurityDto(TypedDict, total=False):
    ticker: str
    custodian: str
    tlhSecurityTicker: str
    priority: int
    isSecuritySetLevel: bool


class BillingSetAsideCashDto(TypedDict, total=False):
    orionConnectExternalAccountId: int
    orionConnectFirmId: int
    amount: float


class DeleteAccountSetAsideCashRequestDto(TypedDict, total=False):
    setAsideIds: list[int]
    skipAnalytics: bool


class DeletePortfolioSetAsideCashRequestDto(TypedDict, total=False):
    setAsideIds: list[int]
    skipAnalytics: bool


class ReverseSyncLogErrorDto(TypedDict, total=False):
    id: int
    reverseSynchLogId: int
    errorMessage: str


class TacticalAccountAndCashDetailsDto(TypedDict, total=False):
    id: int
    portfolioId: int
    accountName: str
    accountId: str
    accountNumber: str
    accountTypeName: str
    taxTypeCode: str
    isDiscretionary: str
    portfolio: str
    custodian: str
    billingAccount: int
    restrictedPlanId: int
    value: float
    managedValue: float
    excludedValue: float
    reserveUsageValue: float
    sleeveType: str
    systematicAmount: float
    systematicDate: str
    sma: str
    createdDate: str
    editedDate: str
    distributionAmount: float
    contributionAmount: float
    pendingTrades: str
    eclipseCreatedDate: str
    mergeIn: float
    mergeOut: float
    disabledReason: str
    custodianRestrictions: str
    isDisabled: bool
    createdBy: str
    editedBy: str
    status: str
    statusReason: str
    style: str
    model: str
    reserveCashTarget: float
    reserveCashActual: float
    setAsideCashMin: float
    setAsideCashTarget: float
    setAsideCashActual: float
    targetCash: float
    targetCashPercent: float
    currentCash: float
    currentCashPercent: float
    pendingCashValue: float
    pendingCashPercent: float
    cashNeedAmount: float
    cashNeedPercent: float
    pendingValue: float
    pendingValuePercent: float
    restrictedPlanName: str
    reserveCashPercent: float
    billingAccountActualCash: float
    billingAccountActualPercent: float
    setAsideCashPercent: float
    setAsideCashMinPercent: float
    modelPlusRebalanceCash: float
    modelPlusRebalancePercent: float
    minCashDollar: float
    maxCashDollar: float
    isDoNotBuySell: str
    minCashToleranceAmount: float
    maxCashToleranceAmount: float
    billingAccountTargetCash: float
    billingAccountTargetPercent: float
    modelName: str
    excludeRebalanceSleeve: bool
    modelId: int
    suffixForSleevedModels: str
    reviewLevel: str
    rebalanceLevel: str
    sleeveTarget: float
    sleeveToleranceLower: float
    sleeveToleranceUpper: float
    postCashValue: float
    originalManagedValue: float
    hasTaxLossHarvest: bool
    accountTags: str
    brokerDealerId: int
    riaId: int
    hasSMAWeighting: int
    billPayMethod: str
    hasContribution: bool
    hasDistribution: bool
    accountSmaAllocations: list[AccountSmaAllocationDto]
    depletionMethod: str
    accountMaxGainIndicatorValue: str
    accountMaxGainValue: str
    rmdAmount: float
    rmdRemaining: float
    distributionAmtYTD: float


class TagDto(TypedDict, total=False):
    tagTypeId: int
    value: str


class CreatedTradesDto(TypedDict, total=False):
    instanceId: int
    tradeId: list[int]
    trades: list[TradeDto]
    excludeTrades: list[ExcludeTradesDto]


class ExcludeTradesDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    securityId: int
    action: int
    message: str
    shortCodes: str


class QuickTradeDto(TypedDict, total=False):
    accountId: int
    accountNumber: str
    portfolioId: int
    actionId: int
    securityId: int
    dollarAmount: float
    quantity: int
    percentage: float
    isSendImmediately: bool
    securitySymbol: str


class TradeRecordDto(TypedDict, total=False):
    error: str
    isValid: bool
    primaryAccountid: int
    accountid: str
    actionId: int
    action: str
    securityId: int
    securityName: str
    dollarAmount: float
    shares: int
    quickTradeDto: QuickTradeDto


class GroupingLevels(TypedDict, total=False):
    level1: str
    level2: str


class ReportData(TypedDict, total=False):
    includeExcludedHolding: bool
    showMaskAccountNumber: bool
    groupingLevels: GroupingLevels


class TradeAnalysisReportParamsDto(TypedDict, total=False):
    tradeIds: list[int]
    reportDataParams: ReportData


class FixedIncomeTradeBlockFailureDto(TypedDict, total=False):
    relatedTypeId: int
    tradeInstanceId: int
    error: str


class FixedIncomeTradeBlockRequestDto(TypedDict, total=False):
    relatedTypeId: int
    tradeInstanceId: int


class FixedIncomeTradeBlockResultDto(TypedDict, total=False):
    succeeded: list[TradeBlockDetailDto]
    failed: list[FixedIncomeTradeBlockFailureDto]


class ManualTradeBlockInfoDto(TypedDict, total=False):
    description: str


class SaveTradeBlockReasonPermissionRequest(TypedDict, total=False):
    tradeBlockReasonId: int
    hasAccess: bool
    canAssignRoles: bool


class SaveTradeBlockReasonRolePermissionsRequest(TypedDict, total=False):
    permissions: list[TradeBlockReasonRolePermissionItem]


class TradeBlockDetailDto(TypedDict, total=False):
    id: int
    relatedType: int
    relatedTypeId: int
    tradeBlockReasonId: int
    description: str
    startDate: str
    endDate: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    isDeleted: bool
    createdByUser: str
    editedByUser: str
    entityName: str
    globalId: str
    associatedModelId: int
    isDisabled: bool
    tradeBlockReason: TradeBlockReasonDto


class TradeBlockDetailsHistoryDto(TypedDict, total=False):
    id: int
    changeType: str
    type: str
    description: str
    createdBy: str
    editedBy: str
    startDate: str
    endDate: str
    createdDate: str
    editedDate: str


class TradeBlockReasonDto(TypedDict, total=False):
    id: int
    name: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    globalId: str
    eclipseFirmId: int
    isSystemMaintained: bool
    allowDetailAssignment: bool
    createdByUser: str
    editedByUser: str
    canManageRolePermissions: bool
    hasRoleAccess: bool


class TradeBlockReasonRolePermissionDto(TypedDict, total=False):
    roleId: int
    roleName: str
    roleType: str
    hasAccess: bool
    canAssignRoles: bool
    isLocked: bool


class TradeBlockReasonRolePermissionItem(TypedDict, total=False):
    roleId: int
    hasAccess: bool
    canAssignRoles: bool


class TradeBlockReasonWithRolePermissionDto(TypedDict, total=False):
    tradeBlockReasonId: int
    reasonName: str
    createdDate: str
    createdByUser: str
    hasAccess: bool
    canAssignRoles: bool
    canManageRolePermissions: bool


class TradeBlockRelatedEntityDto(TypedDict, total=False):
    id: int
    entityType: int
    name: str


class OrderConditionTypeDto(TypedDict, total=False):
    id: int
    name: str


class OrderListDynamicDto(TypedDict, total=False):
    accountId: str
    accountName: str
    accountNumber: str
    accountPostTradeHoldingPercent: float
    accountTags: str
    accountType: str
    accountTypeId: int
    accountValue: float
    action: str
    allocationStatusId: int
    allocationStatusName: str
    assetClassName: str
    blockAllocationStatus: str
    blockCumQty: float
    blockId: int
    blockOrderStatus: str
    canExecute: bool
    canUpdate: bool
    cashOutOfTolerance: str
    cashValue: float
    cashValuePostTrade: float
    cashValuePostTradePercent: float
    createdBy: str
    createdDate: str
    currentModelId: int
    currentModelName: str
    currentYTDGains: float
    custodianId: int
    custodianName: str
    daysUntilLongTerm: int
    defaultTeam: str
    doNotTrade: bool
    durationId: int
    durationName: str
    editedBy: str
    editedDate: str
    estimateAmount: float
    pendingEstimateAmount: float
    estimatedTax: float
    excludedValue: float
    excludeRebalanceSleeve: bool
    execInst: str
    expireTime: str
    fullSetDate: str
    gainLossMessage: str
    handlInst: str
    hasBlock: bool
    hasUnassignedHoldings: str
    holdingId: int
    holdingUnits: float
    holdUntil: str
    idAccount: int
    instanceDescription: str
    instanceId: int
    instanceNotes: str
    isClientDirected: bool
    isDiscretionary: bool
    isEnabled: bool
    isInstanceEnabled: bool
    isLocateRequired: bool
    isMAC: bool
    isPortfolioDisabled: bool
    isSleevePortfolio: bool
    isSolicited: bool
    isTradeable: bool
    longTermCapitalGainTax: float
    longTermGain: float
    managedValue: float
    accountManagementStyle: str
    managementStyle: str
    marketValue: float
    masterAccountNumber: str
    maxGainAmount: float
    managedCashPercent: float
    minCashBalance: float
    modelManagementStyleId: int
    notes: str
    optionExecutionType: int
    optionMaturityDate: str
    optionParentProduct: str
    optionTradesLinkId: str
    optionType: str
    orderModelId: int
    orderModelName: str
    orderPercent: float
    orderQty: float
    orderStatusId: int
    orderStatusName: str
    orderType: str
    orderTypeId: int
    ordinaryIncomeTax: float
    originalEditedDate: str
    originalHoldUntil: str
    originalOrderQty: float
    orionConnectFirmId: int
    outsideId: str
    pendingUnits: str
    portfolioId: int
    portfolioName: str
    portfolioOutOfTolerance: str
    portfolioPostTradeHoldingPercent: float
    postYTDGains: float
    price: float
    qualified: str
    qualifierId: int
    qualifierName: str
    rebalanceLevel: str
    rebalanceLevelId: int
    redemptionFee: float
    reinvestDividends: bool
    reinvestLongTermGains: bool
    reinvestShortTermGains: bool
    representativeName: str
    rowVersion: int
    securityId: int
    securityName: str
    securitySymbol: str
    securityTargetPercentage: float
    securityType: str
    securityTypeId: int
    setAsideCash: float
    settlementName: str
    settlementTypeId: int
    shortCodeMessages: str
    shortTermGain: float
    stopPrice: float
    strikePrice: float
    tags: str
    targetCashPercent: float
    targetCashReserve: float
    timeInForceId: int
    totalGain: float
    totalValue: float
    tradeApprovalLevel: str
    tradeApprovalStatus: str
    tradeApprovalStatusId: int
    tradeBatchId: int
    tradeComplianceStatus: str
    tradeComplianceMessage: str
    tradeExecutionTypeId: int
    tradeId: int
    tradeIdentityUuid: str
    tradeOrderMessageId: int
    tradePercentageOfAccount: float
    tradePercentageOfPortfolio: float
    tradeStatus: str
    tradingInstructions: str
    transactionFee: float
    transactionId: int
    vspDate: str
    vspInfo: bool
    vspPrice: float
    washAmount: float
    washUnits: float
    notesCount: int
    displayNotes: str
    teamNotes: str
    brokerDealerId: int
    riaId: int
    carryForwardLossAmount: float
    accountSweepCash: float
    accountSweepCashPercent: float
    accountMoneyMarketCash: float
    accountMoneyMarketCashPercent: float
    portfolioSweepCash: float
    portfolioSweepCashPercent: float
    portfolioMoneyMarketCash: float
    portfolioMoneyMarketCashPercent: float
    currentShares: float
    representativeId: int
    registrationId: int
    portfolioCashValuePreTradePercent: float
    orderConditionTypeName: str
    accountCashValuePreTradePercent: float
    portfolioCashValuePostTrade: float
    executingBrokerName: str
    executingDestinationName: str
    allocationDestinationName: str
    tradeDate: str
    blockAvgPrice: float
    blockTradeAwayBlockId: int
    managedCashValue: float
    outputColumns: list[str]
    productCategoryName: str
    productSubClassName: str
    outsourcedManager: str
    executingFirm: str
    instanceTypeSubtype: str
    outsourcedStatus: str


class ContributionSleeveTradeDto(TypedDict, total=False):
    fromAccount: str
    fromId: int
    funds: float
    toAccount: str
    toId: int
    sleeveContributionPercent: float
    tradeAmount: float
    portfolioId: int
    portfolioName: str
    accountNumber: str
    needAnalytics: int


class ByFundDistributionAcctData(TypedDict, total=False):
    portfolioId: int
    fullAmount: float
    funds: list[Fund]


class DistributionFullRebalanceDto(TypedDict, total=False):
    sleevedPortfolios: list[FullDistributionAcctData]
    isViewOnly: bool
    isSetAsideCash: bool


class FullDistributionAcctData(TypedDict, total=False):
    id: int
    amount: int


class Fund(TypedDict, total=False):
    accountId: int
    securityId: int
    amount: float
    action: str


class RaiseCashByFundDto(TypedDict, total=False):
    selectedMethodId: int
    sleevedPortfolios: list[ByFundDistributionAcctData]


class TrimBuyTradesRequestDto(TypedDict, total=False):
    tradeIds: list[int]
    trimPercent: float


class TrimBuyTradesResponseDto(TypedDict, total=False):
    tradeId: int
    realTimePrice: float
    updatedQuantity: float
    updatedAmount: float
    partialShares: int
    messages: str
    warningMessage: str


class TrimmedTradeUpdateRequestDto(TypedDict, total=False):
    tradeId: int
    updatedQuantity: float
    updatedAmount: float
    partialShares: int
    messages: str
    warningMessage: str
    realTimePrice: float
    portfolioId: int
    notes: str


class TrimmedTradesUpdateResponseDto(TypedDict, total=False):
    tradeId: int
    updatedQuantity: float
    updatedAmount: float
    editedBy: str
    editedDate: str
    warningMessage: str
    realTimePrice: float
    messages: str
    notes: str


class AccountForAstroTradeDto(TypedDict, total=False):
    accountId: int
    connectFirmId: int


class AstroTradeOrder(TypedDict, total=False):
    batchName: str
    accountIds: list[AccountForAstroTradeDto]


class CreateTradeInstanceRequestDto(TypedDict, total=False):
    tradeTool: int
    tradeParameter: dict[str, Any]


class GenerateAllocationTradeFileRequest(TypedDict, total=False):
    blockIds: list[int]


class OptionAccountInfoRequest(TypedDict, total=False):
    accountIds: list[int]
    symbol: str


class OptionContractRequest(TypedDict, total=False):
    shareQuantity: int
    optionQuantity: int
    accountId: int
    contractName: str
    symbol: str
    tradeAction: int
    lastPrice: float
    optionType: int
    contractAction: int
    strikePrice: float
    expirationDate: str
    instanceNotes: str
    optionTradesLinkId: str
    tradeToolSelection: int
    optionTradeId: int
    validateTradeDto: ValidateTradeDto


class OptionHoldingRequest(TypedDict, total=False):
    accountIds: list[int]


class ProcessTradeDto(TypedDict, total=False):
    tradeIds: list[int]
    instanceIds: list[int]


class SaveAstroTradeOrdersRequest(TypedDict, total=False):
    astroTradeOrders: list[AstroTradeOrder]


class SelectedTradeIdsDto(TypedDict, total=False):
    portfolioId: int
    instanceId: int
    ids: list[int]


class StageAstroTradesRequest(TypedDict, total=False):
    batchName: str
    orionFirmId: int


class SplitBlockRequestDto(TypedDict, total=False):
    blockId: int
    numberOfSubBlocks: int


class TradeAwayBlockRequestDto(TypedDict, total=False):
    blockIds: list[int]
    executingBrokerId: int
    executingDestinationId: int
    allocationDestinationId: int
    isUnderlyingCustodian: bool


class TradeErrorDto(TypedDict, total=False):
    tradeId: int
    errorMessageId: int
    errorMessageArguments: str


class TradeImportPortfolioFlagDto(TypedDict, total=False):
    portfolioId: int
    needAnalytics: bool
    failedReason: str


class TradeImportRequestDto(TypedDict, total=False):
    tradesAreAlreadyValidated: bool
    trades: list[ValidateTradeDto]
    instanceNotes: str


class TradeInstanceUpdateDto(TypedDict, total=False):
    tradeInstanceId: int
    notes: str
    isEnabled: bool
    isDeleted: bool


class TradeOrderMessageDto(TypedDict, total=False):
    id: int
    severityId: int
    shortCode: str
    message: str


class ValidateTradeDto(TypedDict, total=False):
    tradeId: int
    taxLotId: int
    portfolioId: int
    accountId: int
    accountName: str
    accId: int
    orionAccountId: str
    accountNumber: str
    securityId: int
    symbol: str
    tradeInstanceId: int
    custodianId: int
    custodian: str
    positionId: int
    action: int
    orderStatus: int
    warningMessage: str
    zeroTradeReasons: str
    rebalanceLevel: str
    rebalanceLevelId: int
    tradeCreatedDate: str
    isEnabled: bool
    tradeShares: float
    tradePercent: float
    price: float
    tradeAmount: float
    cashValuePostTrade: float
    tradeSTGainLoss: float
    tradeSTGainLossPercent: float
    tradeLTGainLoss: float
    tradeLTGainLossPercent: float
    tradeGainLoss: float
    tradeGainLossPercent: float
    approvalStatus: int
    redemptionFee: float
    transactionFee: float
    totalCost: float
    dateAcquired: str
    washAmount: float
    washAmountPerTaxLot: float
    washUnits: float
    washUnitsPerTaxLot: float
    isSma: bool
    billingAccount: int
    restrictedPlanName: str
    taxableType: int
    costAmount: float
    tradeCostAmount: float
    taxLotPrice: float
    costPerShare: float
    priceDate: str
    securityType: int
    advisorId: int
    severity: int
    tradeCode: int
    orderType: int
    limitPrice: float
    stopPrice: float
    holdUntil: str
    accountValue: float
    cashValue: float
    notes: str
    isClientDirected: bool
    orderStatusId: int
    allocationStatusId: int
    tradeType: int
    orionConnectAccountExternalId: int
    orionConnectFirmId: int
    fixedIncomeTrading: bool
    fixedIncomeTradeBlockDays: int
    instanceNotes: str
    isValid: bool
    validationMessage: str
    isDeleted: bool
    isVsp: bool
    error: list[TradeErrorDto]
    isAggregatedTrade: bool
    aggregateOfTradeIds: list[int]
    taxLotIdBeforeAggregation: int
    orderQtyBeforeAggregation: float
    tradeAmountBeforeAggregation: float
    isUsedForAggregation: bool
    isTradeModified: bool
    isExcludedHolding: bool
    optionContractAction: int
    optionExpirationDate: str
    optionParentSymbol: str
    optionType: int
    strikePrice: float
    optionTradesLinkId: str
    orderLocation: str
    isCashSecurity: bool
    partialShares: int
    origTaxlotQuantity: float
    complianceApprovalStatus: str
    complianceMessage: str
    tradeIdentityUuid: str
    requestId: int
    is100PercentSell: bool
    isTradeFromOtherTradeToolInTactical: bool
    uniqueAggregationId: str
    positionShares: float
    isTradableMoneyMarket: bool
    isLongTerm: int
    isSecurityUnassigned: bool
    orderConditionTypeId: int
    astroTradeId: int
    optionTradeId: int


class ValidateTradeImportDto(TypedDict, total=False):
    portfolioFlag: list[TradeImportPortfolioFlagDto]
    trades: list[ValidateTradeDto]


class ValidateTradeWrapperDto(TypedDict, total=False):
    application: int
    trades: list[ValidateTradeDto]
    instanceNotes: str
    instanceIdForTradeToolsInTactical: int
    tradeToolSelection: int
    tradeInstanceType: int
    tradeInstanceSubType: int


class DTOs_UserGridViewDto(TypedDict, total=False):
    id: int
    viewTypeId: int
    gridColumnDefs: str


class CreateWorkflowContextDto(TypedDict, total=False):
    name: str
    description: str
    workflowDefinition: str
    isSystemWorkflow: bool
    isPublic: bool
    ownerUserId: int
    metadata: dict[str, Any]
    contextTypes: list[str]


class CreateWorkflowContextToolDto(TypedDict, total=False):
    toolName: str
    toolType: str
    description: str
    configuration: dict[str, Any]
    version: str


class UpdateWorkflowContextDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    workflowDefinition: str
    isPublic: bool
    metadata: dict[str, Any]
    contextTypes: list[str]


class WorkflowContextDto(TypedDict, total=False):
    id: int
    name: str
    description: str
    workflowDefinition: str
    isSystemWorkflow: bool
    isPublic: bool
    ownerUserId: int
    ownerUserName: str
    metadata: dict[str, Any]
    contextTypes: list[str]
    createdDate: str
    createdBy: int
    createdByName: str
    editedDate: str
    editedBy: int
    editedByName: str


class WorkflowContextToolDto(TypedDict, total=False):
    id: int
    toolName: str
    toolType: str
    description: str
    configuration: dict[str, Any]
    version: str
    createdDate: str
    createdBy: int
    createdByName: str


class AccountGainLossReportDataDto(TypedDict, total=False):
    proposedNetShortTermGainLoss: float
    proposedNetLongTermGainLoss: float
    proposedTaxCost: float
    remainingShortTermGainLoss: float
    remainingLongTermGainLoss: float


class AccountGainLossReportDto(TypedDict, total=False):
    user_Id: str
    batch_Name: str
    account_Id: str
    proposed_Net_St_Gain_Loss: float
    proposed_Net_Lt_Gain_Loss: float
    proposed_Tax_Cost: float
    remaining_Short_Term_Gain_Loss: float
    remaining_Lt_Gain_Loss: float


class AstroBatchOptimizationRequestDto(TypedDict, total=False):
    ssoAccessToken: str
    ownerID: str
    operation: str
    batchName: str
    accountIds: list[str]
    externalAccountIds: list[int]
    externalAccountIdsInvestCash: list[int]
    maxTrackErr: float
    minTrackErr: float
    maxSecExp: float
    minThreshold: float
    maxTurnover: float
    maxNoOfAssets: float
    defaultTransCostSell: float
    defaultTransCostBuy: float
    ticketCharge: float
    maxCapitalGains: float
    netCapGainYTD: float


class AstroHoldingRestrictionDto(TypedDict, total=False):
    securityId: int
    orionConnectSecurityId: int
    securityType: str
    securityName: str
    ticker: str
    maximumPercent: float
    minimumPercent: float
    accountId: str
    userId: str
    updateSource: str
    restrictionType: int


class AstroOptimizationReportDataDto(TypedDict, total=False):
    topTenDecrease: list[TopTenDto]
    topTenIncrease: list[TopTenDto]
    optGainLoss: AccountGainLossReportDataDto
    portfolioSummary: SubReportPortfolioSummaryDto
    optimizationOperation: list[OptimizationOperationDto]
    optimizationStatus: OptimizationStatusDto


class AstroOptimizationReportDto(TypedDict, total=False):
    topTenDecrease: list[TopTenDto]
    topTenIncrease: list[TopTenDto]
    optGainLoss: AccountGainLossReportDto
    portfolioSummary: SubReportPortfolioSummaryDto


class AstroOptimizationRequestDto(TypedDict, total=False):
    accountIds: list[str]
    optimizationType: int
    isInvestCash: bool
    optimizeOverride: OptimizeOverrideDto
    withdrawCash: WithdrawCashDto


class AstroSingleOptimizationRequestDto(TypedDict, total=False):
    ssoAccessToken: str
    shortTermGainRate: float
    taxAwareSelection: bool
    withholdCashForTaxes: bool
    longTermGainRate: float
    withholdCashForTransactionCosts: bool
    maxTrackErr: float
    maxHoldWt: float
    benchmarkID: str
    defaultTransCostBuy: float
    ticketCharge: float
    minTrackErr: float
    maxTurnover: float
    maxNoOfAssets: float
    minHoldWt: float
    defaultTransCostSell: float
    netCapGainYTD: float
    maxTrades: float
    minTradeSizePCT: float
    maxCapitalGains: float
    orionConnectAccountId: str
    operation: str
    batchName: str
    isInvestCashRestriction: bool


class AstroTlhBatchOptimizationRequestDto(TypedDict, total=False):
    ssoAccessToken: str
    ownerID: str
    batchName: str
    accountIds: list[str]
    externalAccountIds: list[int]
    isAmountToHarvest: int
    isMinTradeSizePCT: int
    isSTLossPCT: int
    isLTLossPCT: int
    isSellLotifLossGTPCT: int
    minTrackErr: float
    maxTrackErr: float
    isRestrictTLH: int
    updateAccountData: bool
    minTradeSize: int
    maxTrades: int
    stLoss: float
    ltLoss: float
    sellLotifLossGT: float


class BatchHoldingSummaryDto(TypedDict, total=False):
    projectName: str
    securityId: str
    ticker: str
    securityName: str
    marketValue: float
    costBasis: float
    acquiredDate: str
    initialShares: float
    finalShares: float
    changeShare: float
    initialPercentOfPortfolio: float
    finalPercentOfPortfolio: float
    transactionValue: float
    tax: float
    realizedGainLoss: float


class BatchStatusDto(TypedDict, total=False):
    batchName: str
    status: str
    isError: bool
    message: str
    uniqueBatchIdentifier: str


class BatchStatusRequestDto(TypedDict, total=False):
    batchIds: list[str]
    connectFirmId: str
    isError: bool


class BenchHoldingSummaryDto(TypedDict, total=False):
    userId: str
    benchId: str
    securityId: str
    securityName: str
    ticker: str
    shares: float
    marketValue: float
    percentWeight: float
    asOfDate: str


class HoldingsAndTargetStrategiesSummaryDto(TypedDict, total=False):
    holdings: dict[str, Any]
    targetStrategyHoldings: list[BenchHoldingSummaryDto]


class OptimizationOperationDto(TypedDict, total=False):
    objective: str
    target: str
    result: str


class OptimizationStatusDto(TypedDict, total=False):
    accountName: str
    targetStrategy: str
    investmentStrategyName: str
    overallOptimizationStatus: bool
    overallOptimizationMessage: str
    exceptionsPassed: bool
    exceptionsPassedMessage: str
    exceptionsPassedDescription: str
    constraintsPassed: bool
    constraintsPassedMessage: str
    constraintsPassedDescription: str
    recommendedTradeCount: int
    hasRecommendedTrades: bool
    recommendedTradeCountMessage: str
    recommendedTradeCountDescription: str
    ytdLongGain: float
    ytdLongLoss: float
    ytdLongNet: float
    ytdShortGain: float
    ytdShortLoss: float
    ytdShortNet: float
    optimizationStartTime: str
    optimizationDurationSeconds: int
    optimizationType: str
    currentCash: float
    currentCashPercentage: float
    endingCash: float
    endingPercentageCash: float


class OptimizeOverrideDto(TypedDict, total=False):
    shortTermGainTaxRatePercent: float
    longTermGainTaxRatePercent: float
    maximumCapitalGains: float
    netCapitalGainsYTD: float
    securityMinimumWeightPercent: float
    securityMaximumWeightPercent: float
    maximumTurnoverPercent: float
    maximumTrackingErrorPercent: float
    minimumTrackingErrorPercent: float
    maximumNoOfTrades: int
    maximumNoOfAssets: float
    sellTradeTransactionCost: float
    buyTradeTransactionCost: float
    ticketCharge: float
    withholdCashForTransactionCost: bool
    withholdCashForTaxes: bool
    applyInvestCashRestriction: bool
    shortTermLoss: float
    longTermLoss: float
    sellLotIfLossGreaterThan: float
    minimumTradeSize: int
    isAmountToHarvest: bool
    isShortTermLossPct: bool
    isLongTermLossPct: bool
    isSellLotIfLossGreaterThanPct: bool
    isRestrictTlh: bool
    onlySellSecurities: bool
    syncAccountsDataWithRealTimePrices: bool
    simpleRounding: bool
    maximumTrackingErrorOverridePercent: float
    ignoreMaximumCapitalGains: bool


class SubReportPortfolioSummaryDto(TypedDict, total=False):
    accountId: str
    initialMarketValue: float
    optimalMarketValue: float
    initialPercentCash: float
    optimalPercentCash: float
    targetPercentCash: float
    initialHoldings: float
    optimalHoldings: float
    targetHoldings: float
    initialTrackingError: float
    optimalTrackingError: float
    initialRSquared: float
    optimalRSquared: float
    initialBeta: float
    optimalBeta: float
    initialRisk: float
    optimalRisk: float
    targetRisk: float
    turnover: float
    initialTaxCost: float
    optimalTaxCost: float
    sold: int
    purchased: int


class TopTenDto(TypedDict, total=False):
    userId: str
    accountId: str
    securityName: str
    initialPercentWeight: float
    optimalPercentWeight: float
    changePercentWeight: float


class WithdrawCashDto(TypedDict, total=False):
    accountId: str
    withdrawAmount: float
    maxCapitalGains: float
    minTradeSizePCT: float
    maxTrades: float
    includeCash: bool
    onlySellSecurities: bool
    simpleRounding: bool


class CreateCustodianAlgoInstructionRequest(TypedDict, total=False):
    custodianAlgoTagInfoId: int
    instruction: str


class UpdateCustodianAlgoInstructionRequest(TypedDict, total=False):
    instruction: str


class NotificationUpdateDto(TypedDict, total=False):
    notificationId: int
    isDeleted: bool


class OAuthTokenResponse(TypedDict, total=False):
    accessToken: str
    refreshToken: str
    expiresIn: int
    tokenType: str
    scopes: list[str]


class Firm_TradeDto(TypedDict, total=False):
    id: int
    portfolioId: int
    securityId: int
    accountId: int
    tradeOrderMessageId: int
    tradeInstanceId: int
    custodianId: int
    custodian: str
    positionId: int
    modelId: int
    advisorId: int
    severity: int
    tradeAmount: float
    action: int
    tradeCode: int
    status: str
    createdDate: str
    isEnabled: bool
    orderQty: float
    orderPercent: float
    price: float
    warningMessage: str
    tradingInstructions: str
    createdBy: int
    editedBy: int
    editedDate: str
    cashValuePostTrade: float
    orderTypeId: int
    limitPrice: float
    stopPrice: float
    qualifierId: int
    durationId: int
    isDiscretionary: int
    isSolicited: bool
    isAutoAllocate: int
    tradeAction: int
    approvalStatus: int
    holdUntil: str
    accountValue: float
    blockId: int
    calculationMethodId: int
    cashValue: float
    instanceId: int
    instanceNotes: str
    reinvestDividends: bool
    reinvestLongTermGains: bool
    reinvestShortTermGains: bool
    settlementTypeId: int
    assetId: int
    assetUnits: int
    hasBlock: bool
    notes: str
    originalOrderQty: float
    rebalanceLevel: int
    rebalanceLevelId: int
    timeInForceId: int
    transactionId: int
    isClientDirected: bool
    vspDate: str
    vspPrice: float
    orderStatusId: int
    allocationStatusId: int
    tradeFileId: int
    daysUntilLongTerm: int
    expireTime: str
    fullSettDate: str
    isLocateRequired: bool
    marketValue: float
    rowVersion: int
    totalGain: float
    tradePercentageOfAccount: float
    minCashBalance: float
    isTransactionFeeIncluded: bool
    isSendImmediately: bool
    isTLH: bool
    redemptionFee: float
    transactionFee: float
    handlInstId: int
    execInst: str
    tradeTypeId: int
    isTradeable: bool
    vspInfo: int
    sellSharesThreshold: int
    reinvestCapitalGains: bool
    nettingQuantity: float
    nettingBlockId: int
    isMac: int
    mutualFundSell: str
    washUnits: float
    washAmount: float
    partialShares: bool
    houseAccountOrder: bool
    parentTradeId: int
    orderConditionTypeId: int


class TradeExecutionTypeSftpConfigDto(TypedDict, total=False):
    tradeExecutionTypeId: int
    transmitMethod: bool
    sftpHost: str
    sftpUsername: str
    sftpPassword: str
    sftpSshPrivateKey: str
    sftpRemotePath: str


class TradeExecutionTypeSftpConfigUpsertDto(TypedDict, total=False):
    sftpHost: str
    sftpUsername: str
    sftpPassword: str
    sftpSshPrivateKey: str
    sftpRemotePath: str


class CreateTradesRequest(TypedDict, total=False):
    correlationId: str
    scenarioId: str
    sleeveAssignmentConfiguration: SleeveAssignmentConfigurationDto
    modelAssignmentConfiguration: ModelAssignmentConfigurationDto
    portfolioDetails: PortfolioDetailDto
    rebalancerSessionData: RebalancerSessionDataDto


class AccountOrPortfolioInfoDto(TypedDict, total=False):
    modelData: ModelDataDto
    allPreferences: AllPreferencesDto


class AccountSurplusCashDto(TypedDict, total=False):
    accountId: int
    surplusCash: float


class AccountsDetailDto(TypedDict, total=False):
    id: int
    amount: float
    setAsideCashAmount: float


class AccountsDto(TypedDict, total=False):
    accountId: int
    orionConnectAccountId: int
    accountNumber: str
    portfolioId: int
    ytdRealizedStgl: float
    custodianId: int
    custodialAccountNumber: str
    advisorId: int
    modelId: int
    modelName: str
    isSMAModel: int
    billingAccount: int
    isSMA: int
    taxableType: str
    isDoNotBuySell: int
    sleeveTarget: float
    sleeveContributionPercent: float
    sleeveDistributionPercent: float
    sleeveType: str
    isDisabled: int
    dynamicModel: int
    smaTradeable: str
    custodianTradeExecutionTypeId: int
    tradeExecutionTypeName: str
    substitutedModelId: int
    substitutedModelName: str
    systematicDate: str
    monthlySystematicWithdrawal: float
    nextMonthlySystematicWithdrawalDate: str
    quarterlySystematicWithdrawal: float
    nextQuarterlySystematicWithdrawalDate: str
    semiAnnualSystematicWithdrawal: float
    nextSemiAnnualSystematicWithdrawalDate: str
    annualSystematicWithdrawal: float
    nextAnnualSystematicWithdrawalDate: str
    systematicPurchase: float
    onlyCreateFractionalShareLiquidationTrades: bool
    nextSystematicPurchaseDate: str
    tradeExecutionTypeId: int
    sleeveToleranceLower: float
    sleeveToleranceUpper: float
    isModelMacEnabled: int
    accountMacStatus: str
    custodianAllowFractionalEquityOrder: int
    custodianFractionalEquityPrecision: int
    astroEnabled: int
    excludeRebalanceSleeve: int
    sleeveStrategyId: str
    sleeveStrategyName: str
    modelSecurityType: str
    modelSecurityTypeId: str
    sleeveStrategyLowerTolerancePercent: float
    sleeveStrategyUpperTolerancePercent: float
    ytdGainLoss: float
    isDeleted: int
    custodianDefaultDepletionMethod: int
    custodialMFDepletionMethod: int


class AllPreferencesDto(TypedDict, total=False):
    generalPreference: list[GeneralPreferenceDto]
    generalPreferenceForAccount: list[GeneralPreferenceForAccountDto]
    securityPreference: list[SecurityPreferenceDto]
    securityPreferenceForAccount: list[SecurityPreferenceForAccountDto]
    redemptionFeePreference: list[RedemptionFeePreferenceDto]
    redemptionFeePreferenceForAccount: list[RedemptionFeePreferenceForAccountDto]
    tradeMaxFeePreference: list[TradeMaxFeePreferenceDto]
    tradeMaxFeePreferenceForAccount: list[TradeMaxFeePreferenceForAccountDto]
    tradeMinFeePreference: list[TradeMinFeePreferenceDto]
    tradeMinFeePreferenceForAccount: list[TradeMinFeePreferenceForAccountDto]
    transactionFeePreference: list[TransactionFeePreferenceDto]
    transactionFeePreferenceForAccount: list[TransactionFeePreferenceForAccountDto]
    dividendReinvestSettingPreference: list[DividendReinvestSettingPreferenceDto]
    dividendReinvestSettingPreferenceForAccount: list[
        DividendReinvestSettingPreferenceForAccountDto
    ]
    custodianRedemptionSettingPreference: list[CustodianRedemptionSettingPreferenceDto]
    custodianRedemptionFeePreferenceForAccount: list[CustodianRedemptionFeePreferenceForAccountDto]
    capGainReinvestSettingPreference: list[CapGainReinvestSettingPreferenceDto]
    capGainReinvestSettingPreferenceForAccount: list[CapGainReinvestSettingPreferenceForAccountDto]
    locationOptimizationPreference: list[LocationOptimizationPreferenceDto]
    tradeSettingPreference: list[TradeSettingPreferenceDto]
    tradeSettingPreferenceForAccount: list[TradeSettingPreferenceForAccountDto]
    locationAlternatesInPreferences: list[LocationAlternatesInPreferencesDto]
    tradeSettingByAccountType: list[TradeSettingByAccountTypeDto]
    securitySettingPreferences: list[SecuritySettingPreferencesDto]


class AlternateSecurityIdsDto(TypedDict, total=False):
    custodianId: int
    relatedType: int
    relatedTypeId: int
    securityId: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int


class BuyBuySellDto(TypedDict, total=False):
    id: int
    portfolioId: int
    securityId: int
    symbol: str
    isBuyBuySell: int
    quantity: float
    totalGainLossAmount: float
    originalQuantity: float


class BuySellBuyDto(TypedDict, total=False):
    id: int
    portfolioId: int
    securityId: int
    symbol: str
    isBuyBuySell: int
    quantity: float
    totalGainLossAmount: float


class BuyTradesWithinThirtyDaysFromTaxableAccountDto(TypedDict, total=False):
    tlhAlternateSymbol: str
    accountId: int


class CapGainReinvestSettingPreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    capGainReinvestTaxable: int
    capGainsReinvestTaxExempt: int
    capGainsReinvestTaxDef: int
    relatedType: int
    relatedTypeId: int


class CapGainReinvestSettingPreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    capGainReinvestTaxable: bool
    capGainsReinvestTaxExempt: bool
    capGainsReinvestTaxDef: bool
    relatedType: int
    relatedTypeId: int


class ComparisonRequest(TypedDict, total=False):
    rebalancerSessionData: RebalancerSessionDataDto
    portfolioDetails: PortfolioDetailDto
    accountOrPortfolioIdToSpecificData: dict[str, Any]
    washSales: WashSaleDto
    rebalancerConstants: RebalancerConstantDto


class CustodianRedemptionFeePreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    custodianRedemptionFeeTypeId: int
    custodianRedemptionFeeAmount: float
    custodianRedemptionFeeMinAmount: float
    custodianRedemptionFeeMaxAmount: float
    custodianRedemptionDays: int
    relatedType: int
    relatedTypeId: int


class CustodianRedemptionSettingPreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    custodianRedemptionFeeTypeId: int
    custodianRedemptionFeeAmount: float
    custodianRedemptionFeeMinAmount: float
    custodianRedemptionFeeMaxAmount: float
    custodianRedemptionDays: int
    relatedType: int
    relatedTypeId: int


class DividendReinvestSettingPreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    taxableDivReInvest: int
    taxDefDivReinvest: int
    taxExemptDivReinvest: int
    relatedType: int
    relatedTypeId: int


class DividendReinvestSettingPreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    taxableDivReInvest: int
    taxDefDivReinvest: int
    taxExemptDivReinvest: int
    relatedType: int
    relatedTypeId: int


class EnumDto(TypedDict, total=False):
    id: int
    name: str


class FilterDto(TypedDict, total=False):
    minimumTradeAmountType: str
    minimumTradeAmount: float
    allowWashSales: bool
    allowShortTermGains: str
    roundEquityRollup: bool
    priorityRanking: str
    method: str
    raiseOrSpendFullAmount: bool
    isSetAsideCash: bool
    rebalanceType: str
    abilityToStopSalesWithRedemptionFeePenalties: bool
    overrideStopTradesWithinXNumberOfDaysOfGoingFromSTGToLTG: bool
    stopTradesWithinXNumberOfDaysFromStgToLtg: int
    overrideBuyMinimumTransactionAmountFalse: bool
    buyMinimumTransactionAmountType: str
    buyMinimumTransactionAmount: float
    overrideSellMinimumTransactionAmount: bool
    sellMinimumTransactionAmountType: str
    sellMinimumTransactionAmount: float
    overrideBuyMaximumTransactionAmount: float
    buyMaximumTransactionAmountType: str
    buyMaximumTransactionAmount: float
    overrideSellMaximumTransactionAmount: bool
    sellMaximumTransactionAmountType: str
    sellMaximumTransactionAmount: float
    overrideMinimumInitialBuyTransactionAmount: bool
    minimumInitialBuyTransactionAmount: float
    overrideTransactionCostLimit: bool
    transactionCostLimit: float
    tacticalRebalanceDoNotSellUnAssignedSecurities: bool
    tacticalRebalanceDoNotRebalanceCash: bool
    maximumCapitalGainsAllowed: str
    maxGainAmount: float
    maxGainAmountType: str
    includeYTDGainLoss: bool
    tacticalRebalanceSecurities: list[str]
    tacticalRebalanceCashProtection: str
    journalAllExcessCashNeeded: bool
    protectSetAsideCashInContributionSleeve: bool
    accountIds: list[int]
    focusedRebalanceType: str
    sleeveContributionOrDistributionMethod: str
    spendCashToolCashProtection: str
    tradeTolerancePercent: float
    rebalanceTarget: str
    sleevePortfolioRebalanceTarget: str
    sleeveTradeTolerancePercent: float
    sleevePortfolioRebalanceLevel: str
    individualSleeveRebalanceMethod: str
    liquidateEquivalents: bool
    liquidateGroupEquivalents: bool
    sleevePortfolioMinCashThreshold: float
    raiseCashIncludeTargetCash: bool
    liquidateUnassignedSecurities: bool
    rebalanceLevelSetting: str
    taxSensitivitySetting: str
    maxShortTermGainAmount: float
    maxShortTermGainAmountType: str


class GeneralPreferenceDto(TypedDict, total=False):
    name: str
    id: int
    value: str
    indicatorValue: str
    optionName: str
    preferenceDefaultValue: str
    preferenceList: str
    defaultValue: str
    relatedType: int
    relatedTypeId: int
    prefOrder: int


class GeneralPreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    name: str
    id: int
    value: str
    indicatorValue: str
    optionName: str
    preferenceDefaultValue: str
    defaultValue: str
    relatedType: int
    relatedTypeId: int
    prefOrder: int


class GroupEquivalentsDto(TypedDict, total=False):
    securitySetId: int
    equivalentSecurityId: int
    isGroupEquivalent: int
    id: int
    securitySetModelDetailId: int
    buyPriority: int
    sellPriority: int
    equivalenceLevel: int
    equivalenceLevelId: int


class HoldUntilTradesDto(TypedDict, total=False):
    accountId: int
    holdUntilTrade: int


class LocationAlternatesInPreferencesDto(TypedDict, total=False):
    securityId: int
    relatedType: int
    relatedTypeId: int
    custodianId: int
    taxableAlternate: int
    taxableSecurityType: str
    taxableSecurityStatus: str
    taxableAssetCategoryId: int
    taxableAssetClassId: int
    taxableAssetSubClassId: int
    taxableSecuritySymbol: str
    isTaxableFixedIncomeTrading: int
    taxDeferredAlternate: int
    taxDeferredSecurityType: str
    taxDeferredSecurityStatus: str
    taxDeferredAssetCategoryId: int
    taxDeferredAssetClassId: int
    taxDeferredAssetSubClassId: int
    taxDeferredSecuritySymbol: str
    isTaxDefFixedIncomeTrading: int
    taxExemptAlternate: int
    taxExemptSecurityType: str
    taxExemptSecurityStatus: str
    taxExemptAssetCategoryId: int
    taxExemptAssetClassId: int
    taxExemptAssetSubClassId: int
    taxExemptSecuritySymbol: str
    isTaxExemptFixedIncomeTrading: int


class LocationOptimizationPreferenceDto(TypedDict, total=False):
    group: str
    displayName: str
    defaultValue: int
    assetType: str
    assetTypeId: int
    value: str
    locationPriorityIndex: float
    relatedType: int
    relatedTypeId: int
    assetTypeName: str


class MacSettingsAssetCategoryLevelDto(TypedDict, total=False):
    portfolioId: int
    modelId: int
    accountId: int
    securityMACWeightId: int
    securitySymbol: str
    securityType: str
    securityStatus: str
    isTaxable: bool
    isTaxDeffered: bool
    isTaxExempted: bool
    isFixedIncomeTrading: bool
    securityCategoryId: int
    securityClassId: int
    securitySubClassId: int
    securityId: int
    rank: int
    weightingPercentage: float
    assetCategoryId: int
    categoryName: str


class MacSettingsAssetClassLevelDto(TypedDict, total=False):
    portfolioId: int
    modelId: int
    accountId: int
    securityMACWeightId: int
    securitySymbol: str
    securityType: str
    securityStatus: str
    isTaxable: bool
    isTaxDeffered: bool
    isTaxExempted: bool
    isFixedIncomeTrading: bool
    securityCategoryId: int
    securityClassId: int
    securitySubClassId: int
    securityId: int
    rank: int
    weightingPercentage: float
    assetClassId: int
    className: str


class MacSettingsAssetSubClassLevelDto(TypedDict, total=False):
    portfolioId: int
    modelId: int
    accountId: int
    securityMACWeightId: int
    securitySymbol: str
    securityType: str
    securityStatus: str
    isTaxable: bool
    isTaxDeffered: bool
    isTaxExempted: bool
    isFixedIncomeTrading: bool
    securityCategoryId: int
    securityClassId: int
    securitySubClassId: int
    securityId: int
    rank: int
    weightingPercentage: float
    assetSubClassId: int
    subclassName: str


class ModelDataDto(TypedDict, total=False):
    modelNodes: list[ModelNodesDto]
    targetSecurities: list[TargetSecuritiesDto]
    tlhSecurities: list[TlhSecuritiesDto]
    securitySetEquivalents: list[SecuritySetEquivalentsDto]
    preferenceLevelEquivalents: list[PreferenceLevelEquivalentsDto]
    groupEquivalents: list[GroupEquivalentsDto]
    securitiesDetail: list[SecuritiesDetailDto]
    alternateSecurityIds: list[AlternateSecurityIdsDto]


class ModelNodesDto(TypedDict, total=False):
    name: str
    modelDetailId: int
    modelAllocation: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    relatedType: str
    relatedTypeId: int
    rebalancePriority: int
    tags: str
    isDeleted: int
    modelId: int
    modelElementId: int
    leftValue: int
    rightValue: int
    rank: int
    levelNumber: int
    assetName: str


class PortfolioDetailDto(TypedDict, total=False):
    taxlots: list[TaxlotDto]
    positions: list[PositionDto]
    accounts: list[AccountsDto]
    portfolioInformation: list[PortfolioInfoDto]
    macSettingsAtAssetCategory: list[MacSettingsAssetCategoryLevelDto]
    macSettingsAtAssetClass: list[MacSettingsAssetClassLevelDto]
    macSettingsAtAssetSubClass: list[MacSettingsAssetSubClassLevelDto]
    setAsideCash: list[SetAsideCashDto]
    buyTradesWithinThirtyDaysFromTaxableAccount: list[
        BuyTradesWithinThirtyDaysFromTaxableAccountDto
    ]
    restrictedPlanByAccount: list[RestrictedPlanByAccountDto]
    holdUntilTrades: list[HoldUntilTradesDto]
    smaAccountWeightings: list[SmaAccountWeightingsDto]
    accountSurplusCash: list[AccountSurplusCashDto]
    sleevePreferences: list[SleevePreferencesDto]


class PortfolioInfoDto(TypedDict, total=False):
    id: int
    name: str
    modelId: int
    isSleevePortfolio: int
    teamId: int
    sleeveContributionMethod: str
    sleeveDistributionMethod: str
    doNotTrade: int
    dynamicModel: int
    tradingInstruction: str
    needAnalytics: int
    substitutedModelId: int
    portfolioMacStatus: str
    isModelMacEnabled: int
    sellEmphasisOn: int
    buyEmphasisOn: int


class PositionDto(TypedDict, total=False):
    accountId: int
    positionId: int
    orionConnectAccountId: int
    accountNumber: str
    isSMA: int
    isTradableMoneyMarket: int
    isUnassigned: bool
    taxableType: str
    securityId: int
    pendingMarketValue: float
    originalMarketValue: float
    pendingQuantity: float
    originalQuantity: float
    symbol: str
    isFixedIncomeTrading: int
    name: str
    isCustodialCash: int
    orionEclipseName: str
    status: str
    securityTypeName: str
    securityTypeId: int
    price: float
    priceType: str
    priceDateTime: str
    holdingAnalyticsId: int
    excludedHoldings: int


class PreferenceLevelEquivalentsDto(TypedDict, total=False):
    id: int
    securitySetId: int
    rank: int
    custodianId: int
    equivalentSecurityId: int
    isGroupEquivalent: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    securitySetModelDetailId: int
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float
    equivalenceLevel: int
    equivalenceLevelId: int


class RebalanceLevelEnumDto(TypedDict, total=False):
    id: int
    rebalanceLevel: str


class RebalancerConstantDto(TypedDict, total=False):
    tradeAction: list[EnumDto]
    orderType: list[EnumDto]
    tradeOrderMessage: list[TradeOrderMessageEnumDto]
    systemSecurities: list[SystemSecurityEnumDto]
    tradeInstance: list[RebalancerTradeInstanceDto]
    orderStatus: list[EnumDto]
    allocationStatus: list[EnumDto]
    accountType: list[EnumDto]
    rebalanceLevel: list[RebalanceLevelEnumDto]
    tradeApproval: list[EnumDto]
    tradeType: list[EnumDto]


class RebalancerFileDetailDto(TypedDict, total=False):
    rebalancerSessionData: RebalancerSessionDataDto
    portfolioDetails: PortfolioDetailDto
    modelData: ModelDataDto
    allPreferences: AllPreferencesDto
    washSales: WashSaleDto
    rebalancerConstants: list[RebalancerConstantDto]


class RebalancerSessionDataDto(TypedDict, total=False):
    correlationId: str
    tradeInstanceId: int
    ocRequestTime: str
    v2UploadRequestTimeToS3: str
    firmId: int
    modelId: int
    tradeOutputFilePath: str
    success: bool
    message: str
    rebalanceType: int
    type: int
    fetchData: bool
    portfolioId: int
    generateTradeLog: bool
    cashMethod: int
    sleeveAccountMethod: int
    sleevePortfolioRebalanceLevel: int
    accountsDetail: list[AccountsDetailDto]
    useDefaultPreferences: bool
    taxSensitivity: TaxSensitivityDto
    filter: FilterDto
    rebalancerTradeLogFilePath: str
    sleeveAccountIds: list[int]
    focusedRebalanceType: int
    tradeToolSelectionId: int
    tradeInstanceType: int
    tradeInstanceSubType: int


class RebalancerTradeInstanceDto(TypedDict, total=False):
    id: int
    description: str
    createdDate: str
    createdBy: int
    editedDate: str
    editedBy: int
    userId: int
    tradecreationStatusId: int
    parameters: str
    tradeStartTime: str
    tradeEndTime: str
    errorMessage: str
    notes: str
    tradingAppID: int
    tradeToolSelectionId: int
    tradeParameter: str
    entityCount: int
    isEnabled: int
    isDeleted: int
    errorPortfolioStatus: str
    errorPortfolioCount: int
    tradeInstanceType: int
    tradeInstanceSubType: int


class RedemptionFeePreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    securityType: str
    redemptionFeeTypeId: str
    redemptionFeeAmount: float
    redemptionFeeDays: int
    redemptionFeeMinAmount: float
    redemptionFeeMaxAmount: float
    relatedType: int
    relatedTypeId: int


class RedemptionFeePreferenceForAccountDto(TypedDict, total=False):
    portfolioId: str
    accountId: str
    custodianID: int
    securityId: int
    securityTypeId: int
    securityType: str
    redemptionFeeTypeId: str
    redemptionFeeAmount: float
    redemptionFeeDays: int
    redemptionFeeMinAmount: float
    redemptionFeeMaxAmount: float
    relatedType: int
    relatedTypeId: int


class RestrictedPlanByAccountDto(TypedDict, total=False):
    portfolioId: int
    accountId: int
    restrictedPlanId: int
    restrictedPlanName: str
    securityId: int
    securitySymbol: str
    doNotBuyGroupEquivalency: int
    buyPriority: int
    sellPriority: int


class SecuritiesDetailDto(TypedDict, total=False):
    securityId: int
    cusipId: str
    isCustodialCash: bool
    securityType: str
    securityPrice: float
    securityPriceDate: str
    securityStatus: str
    securitySymbol: str
    securityTypeId: int
    isMultiAssetClass: int
    isFixedIncomeTrading: int
    assetCategoryId: int
    assetClassId: int
    assetSubClassId: int
    isTradableMoneyMarket: int


class SecurityPreferenceDto(TypedDict, total=False):
    name: str
    defaultValue: str
    minValue: float
    maxValue: float
    value: str
    securityId: int
    isMultiAssetClass: int
    securityType: str
    securityPrice: float
    securityPriceDate: str
    securityStatus: str
    securitySymbol: str
    securityTypeId: int
    relatedType: int
    relatedTypeId: int


class SecurityPreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    name: str
    defaultValue: str
    minValue: float
    maxValue: float
    value: str
    securityId: int
    securityType: str
    securityPrice: float
    securityPriceDate: str
    securityStatus: str
    securitySymbol: str
    securityTypeId: int
    relatedType: int
    relatedTypeId: int


class SecuritySetEquivalentsDto(TypedDict, total=False):
    id: int
    securitySetId: int
    rank: int
    custodianId: int
    equivalentSecurityId: int
    isGroupEquivalent: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    securitySetModelDetailId: int
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float
    equivalenceLevel: int
    equivalenceLevelId: int


class SecuritySettingPreferencesDto(TypedDict, total=False):
    id: int
    name: str
    displayName: str
    defaultValue: str


class SetAsideCashDto(TypedDict, total=False):
    accountId: int
    setAsideCashAmountType: str
    percentCalculationType: str
    cashAmount: float
    minCashAmount: float
    maxCashAmount: float
    portfolioSetAsideCashId: int


class SleevePreferencesDto(TypedDict, total=False):
    optionId: int
    prefValue: str
    optionOrder: int
    name: str


class SmaAccountWeightingsDto(TypedDict, total=False):
    accountId: int
    accountNumber: str
    id: int
    modelDetailId: int
    modelId: int
    modelNodeName: str
    orionConnectAccountId: int
    weightPercent: float


class SystemSecurityEnumDto(TypedDict, total=False):
    id: int
    symbol: str


class TargetSecuritiesDto(TypedDict, total=False):
    modelAllocation: float
    lowerModelTolerancePercent: float
    upperModelTolerancePercent: float
    securitySetId: int
    rank: int
    custodianId: int
    taxableSecurityId: int
    taxDeferredSecurityId: int
    taxExemptSecurityId: int
    minTradeAmount: float
    minInitialBuyDollar: float
    buyPriority: int
    sellPriority: int
    taxSecuritySymbol: str
    taxDeferredSecuritySymbol: str
    taxExemptSecuritySymbol: str
    taxSecurityAssetCategoryId: int
    isTaxableFixedIncomeTrading: int
    taxDeferredSecurityAssetCategoryId: int
    isTaxDefFixedIncomeTrading: int
    taxExemptSecurityAssetCategoryId: int
    isTaxExemptFixedIncomeTrading: int
    taxSecurityAssetClassId: int
    taxDeferredSecurityAssetClassId: int
    taxExemptSecurityAssetClassId: int
    taxSecurityAssetSubClassId: int
    taxDeferredSecurityAssetSubClassId: int
    taxExemptSecurityAssetSubClassId: int
    taxSecurityType: str
    taxDeferredSecurityType: str
    taxExemptSecurityType: str
    taxSecurityStatus: str
    taxDeferredSecurityStatus: str
    taxExemptSecurityStatus: str
    symbol: str
    assetCategoryId: int
    assetClassId: int
    assetSubClassId: int
    isFixedIncomeTrading: int
    id: int
    securityStatus: str
    isCustodialCash: int
    securityType: str
    securitySetModelDetailId: int
    taxableMinTradeAmount: float
    taxableMinInitialBuyDollar: float
    taxDeferredMinTradeAmount: float
    taxDeferredMinInitialBuyDollar: float
    taxExemptMinTradeAmount: float
    taxExemptMinInitialBuyDollar: float


class TaxSensitivityDto(TypedDict, total=False):
    name: str
    id: int
    value: str
    indicatorValue: str
    optionName: str
    preferenceDefaultValue: str
    defaultValue: str
    relatedType: int
    relatedTypeId: int
    prefOrder: int


class TaxlotDto(TypedDict, total=False):
    taxlotId: int
    accountId: int
    orionConnectAccountId: int
    accountNumber: str
    isSMA: int
    taxableType: str
    securityId: int
    symbol: str
    dateAcquired: str
    orginalQuantity: float
    costPerShare: float
    originalMarketValue: float
    securityType: str
    pendingQuantity: float
    pendingMarketValue: float
    taxLotAnalyticsId: int
    taxlotTypeId: int
    isLongTerm: int
    isSettled: int
    costBasisMethod: int


class TlhSecuritiesDto(TypedDict, total=False):
    securitySetModelDetailId: int
    securitySetId: int
    targetSecurityId: int
    targetSecuritySymbol: str
    tlhCustodianId: int
    tlhSecurityId: int
    tlhSecuritySymbol: str
    tlhAssetCategoryId: int
    tlhAssetClassId: int
    tlhAssetSubClassId: str
    tlhSecurityType: str
    tlhSecurityStatus: str
    isTLHFixedIncomeTrading: bool


class TradeMaxFeePreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    sellTradeMaxAmtBySecurity: float
    sellTradeMaxPctBySecurity: float
    buyTradeMaxAmtBySecurity: float
    buyTradeMaxPctBySecurity: float
    relatedType: int
    relatedTypeId: int


class TradeMaxFeePreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    sellTradeMaxAmtBySecurity: float
    sellTradeMaxPctBySecurity: float
    buyTradeMaxAmtBySecurity: float
    buyTradeMaxPctBySecurity: float
    relatedType: int
    relatedTypeId: int


class TradeMinFeePreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    sellTradeMinAmtBySecurity: float
    sellTradeMinPctBySecurity: float
    buyTradeMinAmtBySecurity: float
    buyTradeMinPctBySecurity: float
    relatedType: int
    relatedTypeId: int


class TradeMinFeePreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    sellTradeMinAmtBySecurity: float
    sellTradeMinPctBySecurity: float
    buyTradeMinAmtBySecurity: float
    buyTradeMinPctBySecurity: float
    relatedType: int
    relatedTypeId: int


class TradeOrderMessageEnumDto(TypedDict, total=False):
    id: int
    shortCode: str


class TradeSettingByAccountTypeDto(TypedDict, total=False):
    accountId: int
    accountTaxableTypeId: int
    accountTaxableType: str
    securityId: int
    buyPriority: int
    sellPriority: int


class TradeSettingPreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    buyPriority: int
    sellPriority: int
    excludedFromTrading: int
    relatedType: int
    relatedTypeId: int


class TradeSettingPreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    buyPriority: int
    sellPriority: int
    excludedFromTrading: int
    relatedType: int
    relatedTypeId: int


class TransactionFeePreferenceDto(TypedDict, total=False):
    securityId: int
    securityTypeId: int
    buyTransactionFee: float
    sellTransactionFee: float
    relatedType: int
    relatedTypeId: int


class TransactionFeePreferenceForAccountDto(TypedDict, total=False):
    accountId: int
    portfolioId: int
    custodianId: int
    securityId: int
    securityTypeId: int
    buyTransactionFee: float
    sellTransactionFee: float
    relatedType: int
    relatedTypeId: int


class WashSaleDto(TypedDict, total=False):
    buyBuySell: list[BuyBuySellDto]
    buySellBuy: list[BuySellBuyDto]


class ModelAssignmentConfigurationDto(TypedDict, total=False):
    modelId: int
    portfolioId: int


class AccountSleeveMinimalDto(TypedDict, total=False):
    accountId: int
    registrationId: int
    targetAllocation: float
    currentAllocation: float
    currentValue: float
    contributionAllocation: float
    distributionAllocation: float
    toleranceLower: float
    toleranceUpper: float
    modelAgg: str
    modelAggId: int
    modelAggType: int
    modelAggMinimumInvestmentAmount: float
    subAdvisor: str
    subAdvisorId: int
    doNotTrade: bool
    sleeveStrategyDetailId: int
    sleeveStrategy: str
    sleeveStrategyId: int
    sleeveStrategyToleranceLower: float
    sleeveStrategyToleranceUpper: float
    riskScore: float
    modelAllocations: list[ModelItemFullDto]
    assets: list[AssetDto]
    defaultSleeve: bool
    name: str
    sleeveType: str
    guid: str
    autoRebalanceSelfDirected: bool
    deductFeesFromProductId: int
    managementStyleId: int


class AssetDto(TypedDict, total=False):
    id: int
    costBasis: float
    name: str
    accountNumber: str
    ticker: str
    currentShares: float
    currentValue: float
    currentPrice: float
    isManaged: bool
    assetClass: str
    productCategory: str
    productCategoryAbbreviation: str
    isCustodialCash: bool
    secondaryAccountNumber: str
    cusip: str
    productId: int
    assetLevelStrategyId: int
    assetLevelStrategy: str
    status: int
    isStrategyOverride: bool
    createdBy: str
    createdDate: str
    editedBy: str
    editedDate: str
    accountId: int
    registrationId: int
    clientId: int
    isActive: bool
    downloadSymbol: int
    accountType: str
    fundFamily: str
    custodian: str
    asOfDate: str
    registrationName: str
    managementStyle: str
    sleeveType: str
    productType: str
    productSubType: str
    isGlobalExcluded: bool
    isFeeExcluded: bool
    excludeAmountType: str
    excludeAmount: float
    excludePercentOf: str
    isRebalance: bool
    isAdvisorOnly: bool
    isAdvReportable: bool
    is13FReportable: bool
    mscsFundAccountNumber: str
    lastReconDate: str
    isOrionVision: bool
    assetPercentOfAccount: float
    householdName: str
    riskCategory: str
    modelName: str
    registrationType: str
    accountStatusId: int


class AstroAccountTaxSchedulesDto(TypedDict, total=False):
    accountId: int
    year: int
    annualCapGain: float
    q1Percent: float
    q2Percent: float
    q3Percent: float
    q4Percent: float


class AstroAssetDto(TypedDict, total=False):
    assetId: int
    productId: int
    accountId: int
    productName: str
    source: str
    restrictionType: int
    isCustodialCash: bool
    minPercentWeight: float
    maxPercentWeight: float
    ticker: str
    shares: float
    allocation: float


class AstroSleeveDto(TypedDict, total=False):
    id: int
    type: str
    number: str
    useCustodialRestrictions: bool
    restrictionStatus: str


class EsgCategoryRestrictionDto(TypedDict, total=False):
    esgCategoryId: int
    name: str
    isExcluded: bool


class Sleeves_IndustryDto(TypedDict, total=False):
    id: str
    name: str
    penalty: float
    minimumValue: float
    maximumValue: float
    sectorId: str


class ModelItemFullDto(TypedDict, total=False):
    id: int
    productId: int
    productName: str
    productClass: str
    ticker: str
    targetPercent: float
    itemTol: int
    createdDate: str
    createdBy: str
    editedDate: str
    editedBy: str
    itemTolUpper: float
    itemTolLower: float
    oub: float
    modelAggId: int
    productRiskScore: int


class RegistrationSleeveMinimalDto(TypedDict, total=False):
    sleeveStrategyId: int
    sleeveStrategyAggId: int
    custodialAccountNumber: str
    registrationId: int
    currentValue: float
    isDoNotTrade: bool
    eclipseFirmId: int
    clientId: int
    eclipseFirm: str
    riskTolerance: float
    autoRebalFrequency: str
    autoRebalMonth: int
    autoRebalDay: int
    contributionAllocationMethod: str
    distributionAllocationMethod: str
    isActive: bool
    lastRebalanceDate: str


class RetAstroAccountDto(TypedDict, total=False):
    id: int
    astroTemplate: str
    maxRealizedGain: float
    fedShortTaxRate: float
    fedLongTaxRate: float
    shortTermTaxRate: float
    longTermTaxRate: float
    ticketCharge: float
    maxTrackingError: float
    minTrackingError: float
    assets: list[AstroAssetDto]
    sectors: list[RetAstroSectorDto]
    sleeves: list[AstroSleeveDto]
    esgRestriction: list[EsgCategoryRestrictionDto]
    astroTaxSchedules: list[AstroAccountTaxSchedulesDto]
    modelAgg: str
    modelAggId: int


class RetAstroSectorDto(TypedDict, total=False):
    id: str
    name: str
    penalty: float
    minimumValue: float
    maximumValue: float
    sectorId: str
    error: bool


class Sleeves_SectorDto(TypedDict, total=False):
    id: str
    name: str
    penalty: str
    minimumValue: float
    maximumValue: float
    industries: list[Sleeves_IndustryDto]


class SleeveAssignmentConfigurationDto(TypedDict, total=False):
    requestedById: str
    registrationSleeve: RegistrationSleeveMinimalDto
    sleevedAccounts: list[AccountSleeveMinimalDto]
    astroAccounts: list[RetAstroAccountDto]
    tradeQueueRebalanceNeeded: bool


class AfterMarketTradingPreferenceUpdateRequest(TypedDict, total=False):
    tradeStartTime: str
    fullDayCutoffTime: str
    halfDayCutoffTime: str
    firmId: int
