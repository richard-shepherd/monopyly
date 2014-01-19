
:: The StartOfTournamentMessage object...
protoc -I=. --python_out=. StartOfTournamentMessage.proto
protogen -i:StartOfTournamentMessage.proto -o:StartOfTournamentMessage.cs

:: The PlayerInfoMessage object...
protoc -I=. --python_out=. PlayerInfoMessage.proto
protogen -i:PlayerInfoMessage.proto -o:PlayerInfoMessage.cs

:: The BoardUpdateMessage object...
protoc -I=. --python_out=. BoardUpdateMessage.proto
protogen -i:BoardUpdateMessage.proto -o:BoardUpdateMessage.cs

