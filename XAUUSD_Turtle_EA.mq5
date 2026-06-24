//+------------------------------------------------------------------+
//|                                           XAUUSD_Turtle_EA.mq5    |
//|                  Trend Following EA inspired by Turtle Trading    |
//|                              (Richard Dennis / Donchian breakout) |
//+------------------------------------------------------------------+
#property copyright "Wing-Master"
#property version   "1.00"
#property strict
#property description "Trend Following EA for XAUUSD - Turtle style breakout (Multi-Timeframe)"
#property description "EMA200 trend filter (HTF) + Donchian breakout/ADX/ATR (entry TF) + ATR risk sizing"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input double          RiskPercent      = 1.0;          // Risque par trade (% du capital)
input int             EMA_Period       = 200;          // Periode EMA (filtre de tendance)
input int             Breakout_Period  = 20;           // Periode breakout (Donchian)
input int             ADX_Period       = 14;           // Periode ADX
input double          ADX_Min          = 25.0;         // Seuil ADX minimum
input int             ATR_Period       = 14;           // Periode ATR
input double          ATR_Multiplier   = 2.0;          // Multiplicateur ATR pour le SL
input double          Reward_Ratio     = 3.0;          // Ratio Risque/Recompense (TP = R x ratio)
input int             MaxSpreadPoints  = 50;           // Spread maximum autorise (points)
input ulong           MagicNumber      = 20260624;     // Magic number
input ENUM_TIMEFRAMES TradeTimeframe   = PERIOD_H1;    // Timeframe d'entree (breakout/ADX/ATR)
input ENUM_TIMEFRAMES TrendTimeframe   = PERIOD_H4;    // Timeframe de tendance (EMA - HTF)
input bool            UseTrendTF       = true;         // Activer le filtre de tendance multi-TF

//+------------------------------------------------------------------+
//| Globals                                                          |
//+------------------------------------------------------------------+
CTrade   trade;

int      hEMA  = INVALID_HANDLE;   // handle iMA (sur le timeframe de tendance HTF)
int      hADX  = INVALID_HANDLE;   // handle iADX (sur le timeframe d'entree)
int      hATR  = INVALID_HANDLE;   // handle iATR (sur le timeframe d'entree)

ENUM_TIMEFRAMES g_trendTF = PERIOD_CURRENT;  // timeframe effectif du filtre de tendance
datetime g_lastBarTime    = 0;               // pour ne traiter qu'une fois par bougie close

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // --- Validation des inputs ---
   if(RiskPercent <= 0.0)
   {
      Print("ERREUR INIT: RiskPercent doit etre > 0.");
      return(INIT_PARAMETERS_INCORRECT);
   }
   if(EMA_Period < 1 || Breakout_Period < 1 || ADX_Period < 1 || ATR_Period < 1)
   {
      Print("ERREUR INIT: les periodes doivent etre >= 1.");
      return(INIT_PARAMETERS_INCORRECT);
   }
   if(ATR_Multiplier <= 0.0 || Reward_Ratio <= 0.0)
   {
      Print("ERREUR INIT: ATR_Multiplier et Reward_Ratio doivent etre > 0.");
      return(INIT_PARAMETERS_INCORRECT);
   }

   // --- Choix du timeframe de tendance (HTF si multi-TF active, sinon le TF d'entree) ---
   g_trendTF = (UseTrendTF ? TrendTimeframe : TradeTimeframe);

   // Le TF de tendance doit etre >= au TF d'entree pour avoir du sens
   if(UseTrendTF && PeriodSeconds(TrendTimeframe) < PeriodSeconds(TradeTimeframe))
   {
      PrintFormat("ATTENTION: TrendTimeframe (%s) est inferieur au TradeTimeframe (%s). "
                  "Le filtre multi-TF perd son sens.",
                  EnumToString(TrendTimeframe), EnumToString(TradeTimeframe));
   }

   // --- Creation des indicateurs ---
   // EMA sur le timeframe de tendance (HTF), breakout/ADX/ATR sur le TF d'entree
   hEMA = iMA(_Symbol, g_trendTF, EMA_Period, 0, MODE_EMA, PRICE_CLOSE);
   hADX = iADX(_Symbol, TradeTimeframe, ADX_Period);
   hATR = iATR(_Symbol, TradeTimeframe, ATR_Period);

   if(hEMA == INVALID_HANDLE || hADX == INVALID_HANDLE || hATR == INVALID_HANDLE)
   {
      Print("ERREUR INIT: impossible de creer un handle d'indicateur. EMA=", hEMA,
            " ADX=", hADX, " ATR=", hATR);
      return(INIT_FAILED);
   }

   // --- Configuration de CTrade ---
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(20);

   PrintFormat("INIT OK | Symbole=%s | EntryTF=%s | TrendTF=%s(EMA%d) | Breakout=%d | ADX=%d(min %.1f) | ATR=%d x%.1f | RR=%.1f | Risk=%.2f%% | Magic=%I64u",
               _Symbol, EnumToString(TradeTimeframe), EnumToString(g_trendTF), EMA_Period,
               Breakout_Period, ADX_Period, ADX_Min, ATR_Period, ATR_Multiplier, Reward_Ratio,
               RiskPercent, MagicNumber);

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(hEMA != INVALID_HANDLE) IndicatorRelease(hEMA);
   if(hADX != INVALID_HANDLE) IndicatorRelease(hADX);
   if(hATR != INVALID_HANDLE) IndicatorRelease(hATR);

   PrintFormat("DEINIT | raison=%d", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // --- Ne travailler qu'a l'ouverture d'une nouvelle bougie ---
   datetime curBarTime = (datetime)SeriesInfoInteger(_Symbol, TradeTimeframe, SERIES_LASTBAR_DATE);
   if(curBarTime == g_lastBarTime)
      return;
   g_lastBarTime = curBarTime;

   // --- Un seul trade ouvert a la fois (meme magic / meme symbole) ---
   if(HasOpenPosition())
      return;

   // --- Verification du spread ---
   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > MaxSpreadPoints)
   {
      PrintFormat("Trade ignore: spread trop eleve (%d > %d points).", (int)spread, MaxSpreadPoints);
      return;
   }

   // --- Lecture des indicateurs (sur la bougie cloturee, index 1) ---
   double emaBuf[1], adxBuf[1], atrBuf[1];

   if(CopyBuffer(hEMA, 0, 1, 1, emaBuf) < 1 ||
      CopyBuffer(hADX, 0, 1, 1, adxBuf) < 1 ||
      CopyBuffer(hATR, 0, 1, 1, atrBuf) < 1)
   {
      Print("Donnees indicateurs non pretes, attente de la prochaine bougie.");
      return;
   }

   double ema = emaBuf[0];
   double adx = adxBuf[0];
   double atr = atrBuf[0];

   if(atr <= 0.0)
   {
      Print("ATR invalide (<=0), trade ignore.");
      return;
   }

   // --- Filtre ADX ---
   if(adx <= ADX_Min)
   {
      // pas de tendance suffisante - rien a faire
      return;
   }

   // --- Plus haut / plus bas des Breakout_Period bougies cloturees (index 1..N) ---
   double hh = HighestHigh(Breakout_Period, 1);
   double ll = LowestLow(Breakout_Period, 1);
   if(hh <= 0.0 || ll <= 0.0)
   {
      Print("Donnees High/Low non disponibles, trade ignore.");
      return;
   }

   // --- Prix courants ---
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   // --- Filtre de tendance MULTI-TIMEFRAME ---
   // L'EMA est calculee sur g_trendTF ; on compare au close de la derniere
   // bougie cloturee de CE meme timeframe pour rester coherent.
   double trendClose = iClose(_Symbol, g_trendTF, 1);
   if(trendClose <= 0.0)
   {
      Print("Close du timeframe de tendance non disponible, trade ignore.");
      return;
   }

   // --- Conditions Turtle ---
   bool trendUp   = (trendClose > ema);
   bool trendDown = (trendClose < ema);

   // close du TF d'entree pour confirmer la cassure
   double lastClose = iClose(_Symbol, TradeTimeframe, 1);

   bool breakoutUp   = (lastClose > hh) || (ask > hh);   // cassure du plus haut
   bool breakoutDown = (lastClose < ll) || (bid < ll);   // cassure du plus bas

   // --- BUY ---
   if(trendUp && breakoutUp && adx > ADX_Min)
   {
      double slDist = ATR_Multiplier * atr;
      double sl     = NormalizePrice(ask - slDist);
      double tp     = NormalizePrice(ask + Reward_Ratio * slDist);
      OpenTrade(ORDER_TYPE_BUY, ask, sl, tp, atr, adx, hh, ll);
      return;
   }

   // --- SELL ---
   if(trendDown && breakoutDown && adx > ADX_Min)
   {
      double slDist = ATR_Multiplier * atr;
      double sl     = NormalizePrice(bid + slDist);
      double tp     = NormalizePrice(bid - Reward_Ratio * slDist);
      OpenTrade(ORDER_TYPE_SELL, bid, sl, tp, atr, adx, hh, ll);
      return;
   }
}

//+------------------------------------------------------------------+
//| Verifie s'il existe deja une position avec ce magic/symbole      |
//+------------------------------------------------------------------+
bool HasOpenPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == MagicNumber)
         return(true);
   }
   return(false);
}

//+------------------------------------------------------------------+
//| Plus haut sur 'count' bougies a partir de l'index 'start'        |
//+------------------------------------------------------------------+
double HighestHigh(const int count, const int start)
{
   double highs[];
   ArraySetAsSeries(highs, true);
   if(CopyHigh(_Symbol, TradeTimeframe, start, count, highs) < count)
      return(0.0);

   double maxH = highs[0];
   for(int i = 1; i < count; i++)
      if(highs[i] > maxH)
         maxH = highs[i];
   return(maxH);
}

//+------------------------------------------------------------------+
//| Plus bas sur 'count' bougies a partir de l'index 'start'         |
//+------------------------------------------------------------------+
double LowestLow(const int count, const int start)
{
   double lows[];
   ArraySetAsSeries(lows, true);
   if(CopyLow(_Symbol, TradeTimeframe, start, count, lows) < count)
      return(0.0);

   double minL = lows[0];
   for(int i = 1; i < count; i++)
      if(lows[i] < minL)
         minL = lows[i];
   return(minL);
}

//+------------------------------------------------------------------+
//| Normalise un prix selon le nombre de digits du symbole           |
//+------------------------------------------------------------------+
double NormalizePrice(const double price)
{
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   return(NormalizeDouble(price, digits));
}

//+------------------------------------------------------------------+
//| Calcule le volume selon le risque et la distance de SL           |
//+------------------------------------------------------------------+
double CalculateLot(const double slDistancePrice)
{
   if(slDistancePrice <= 0.0)
      return(0.0);

   double balance   = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskMoney = balance * RiskPercent / 100.0;

   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

   if(tickValue <= 0.0 || tickSize <= 0.0)
   {
      Print("CalculateLot: tickValue/tickSize invalide.");
      return(0.0);
   }

   // Perte (en devise du compte) pour 1 lot si le SL est touche
   double lossPerLot = (slDistancePrice / tickSize) * tickValue;
   if(lossPerLot <= 0.0)
      return(0.0);

   double lot = riskMoney / lossPerLot;

   // --- Normalisation selon les contraintes du broker ---
   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(lotStep > 0.0)
      lot = MathFloor(lot / lotStep) * lotStep;

   if(lot < minLot) lot = minLot;
   if(lot > maxLot) lot = maxLot;

   // Arrondi au pas pour eviter les erreurs d'arrondi flottant
   int lotDigits = 2;
   if(lotStep > 0.0)
      lotDigits = (int)MathMax(0, MathRound(-MathLog10(lotStep)));
   lot = NormalizeDouble(lot, lotDigits);

   return(lot);
}

//+------------------------------------------------------------------+
//| Ouvre un trade BUY ou SELL                                       |
//+------------------------------------------------------------------+
void OpenTrade(const ENUM_ORDER_TYPE type, const double price,
               double sl, double tp, const double atr,
               const double adx, const double hh, const double ll)
{
   double slDist = MathAbs(price - sl);
   if(slDist <= 0.0)
   {
      Print("OpenTrade: distance SL nulle, annulation.");
      return;
   }

   // --- Respect de la distance minimale (stops level) du broker ---
   long   stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double point      = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double minDist    = stopsLevel * point;

   if(minDist > 0.0 && slDist < minDist)
   {
      PrintFormat("OpenTrade: SL trop proche (%.5f < min %.5f), trade ignore.", slDist, minDist);
      return;
   }

   double lot = CalculateLot(slDist);
   if(lot <= 0.0)
   {
      Print("OpenTrade: volume calcule nul, trade ignore.");
      return;
   }

   sl = NormalizePrice(sl);
   tp = NormalizePrice(tp);

   bool ok = false;
   if(type == ORDER_TYPE_BUY)
   {
      ok = trade.Buy(lot, _Symbol, 0.0, sl, tp, "Turtle BUY");
   }
   else if(type == ORDER_TYPE_SELL)
   {
      ok = trade.Sell(lot, _Symbol, 0.0, sl, tp, "Turtle SELL");
   }

   if(ok)
   {
      PrintFormat("%s OUVERT | lot=%.2f | prix=%.5f | SL=%.5f | TP=%.5f | ATR=%.5f | ADX=%.1f | HH20=%.5f | LL20=%.5f | retcode=%u",
                  (type == ORDER_TYPE_BUY ? "BUY" : "SELL"),
                  lot, price, sl, tp, atr, adx, hh, ll, trade.ResultRetcode());
   }
   else
   {
      PrintFormat("ECHEC ouverture %s | retcode=%u (%s) | lot=%.2f SL=%.5f TP=%.5f",
                  (type == ORDER_TYPE_BUY ? "BUY" : "SELL"),
                  trade.ResultRetcode(), trade.ResultRetcodeDescription(), lot, sl, tp);
   }
}
//+------------------------------------------------------------------+
