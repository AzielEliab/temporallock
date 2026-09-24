import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';

import 'theme.dart';

const genesisPrev = '0000000000000000000000000000000000000000000000000000000000000000';

void main() {
  runApp(const TemporalLockApp());
}

class TemporalLockApp extends StatelessWidget {
  const TemporalLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TemporalLock',
      debugShowCheckedModeBanner: false,
      theme: buildLightTheme(),
      darkTheme: buildDarkTheme(),
      themeMode: ThemeMode.system,
      home: const ChainPage(),
    );
  }
}

class Receipt {
  Receipt({
    required this.timestamp,
    required this.summary,
    required this.evidence,
    required this.confidence,
    required this.prevHash,
    required this.hash,
  });
  final String timestamp;
  final String summary;
  final String evidence;
  final double confidence;
  final String prevHash;
  final String hash;

  bool get hashOk => recompute() == hash;

  String recompute() => digest(timestamp, summary, evidence, confidence, prevHash);
}

String _conf(double c) => c.toStringAsFixed(6);

String digest(String ts, String summary, String evidence, double confidence, String prev) {
  // Canonical: sorted keys, no extra whitespace, confidence 6 decimals unquoted.
  final raw =
      '{"confidence":${_conf(confidence)},"evidence":${jsonEncode(evidence)},"prev_hash":${jsonEncode(prev)},"summary":${jsonEncode(summary)},"timestamp":${jsonEncode(ts)}}';
  return sha256.convert(utf8.encode(raw)).toString();
}

class ChainPage extends StatefulWidget {
  const ChainPage({super.key});

  @override
  State<ChainPage> createState() => _ChainPageState();
}

class _ChainPageState extends State<ChainPage> {
  final _summary = TextEditingController();
  final _evidence = TextEditingController();
  final _confidence = TextEditingController(text: '0.7');
  final _chain = <Receipt>[];
  String _status = 'No receipts yet. Write the first one below.';

  @override
  void dispose() {
    _summary.dispose();
    _evidence.dispose();
    _confidence.dispose();
    super.dispose();
  }

  String _now() => DateTime.now().toUtc().toIso8601String().split('.').first + 'Z';

  void _write() {
    final evidence = _evidence.text;
    if (evidence.trim().isEmpty) {
      setState(() => _status = 'Evidence is required. Add a note or a path, then try again.');
      return;
    }
    final conf = double.tryParse(_confidence.text);
    if (conf == null || conf < 0 || conf > 1) {
      setState(() => _status = 'Confidence needs to be a number from 0 to 1. Set it under Advanced, then try again.');
      return;
    }
    final genesis = _chain.isEmpty;
    final ts = _now();
    final prev = genesis ? genesisPrev : _chain.last.hash;
    final h = digest(ts, _summary.text, evidence, conf, prev);
    setState(() {
      _chain.add(Receipt(
        timestamp: ts,
        summary: _summary.text,
        evidence: evidence,
        confidence: conf,
        prevHash: prev,
        hash: h,
      ));
      _summary.clear();
      _evidence.clear();
      _status = genesis
          ? 'First receipt saved. Add another when you have a new observation.'
          : 'Receipt added. Earlier receipts stay as they were.';
    });
  }

  String _runVerify() {
    if (_chain.isEmpty) return 'No receipts yet. Write the first one, then check links.';
    for (var i = 0; i < _chain.length; i++) {
      final r = _chain[i];
      if (!r.hashOk) return 'These receipts do not link. The hash at $i does not match. Next: add a correction as a new receipt.';
      final expectPrev = i == 0 ? genesisPrev : _chain[i - 1].hash;
      if (r.prevHash != expectPrev) return 'These receipts do not link. The link at $i is broken. Next: add a correction as a new receipt.';
    }
    final n = _chain.length;
    final noun = n == 1 ? 'receipt' : 'receipts';
    return 'Links check out. $n $noun on this chain.';
  }

  @override
  Widget build(BuildContext context) {
    final primary = _chain.isEmpty ? 'Write first receipt' : 'Add receipt';
    return Scaffold(
      appBar: AppBar(
        title: const Text('TemporalLock'),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: Center(child: Text('Aziel Eliab')),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        children: [
          Text('Record a receipt', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          const Text('Write what you observed. TemporalLock keeps it on this device.'),
          const SizedBox(height: 16),
          TextField(controller: _summary, decoration: const InputDecoration(labelText: 'Summary')),
          const SizedBox(height: 8),
          TextField(
            controller: _evidence,
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'Evidence', alignLabelWithHint: true),
          ),
          const SizedBox(height: 12),
          FilledButton(onPressed: _write, child: Text(primary)),
          const SizedBox(height: 12),
          Text(_status),
          const SizedBox(height: 16),
          Text('Receipts', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          if (_chain.isEmpty) const Text('Nothing recorded on this device yet.'),
          for (var i = 0; i < _chain.length; i++)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  [
                    '#$i  ${_chain[i].timestamp}',
                    _chain[i].summary,
                    _chain[i].evidence,
                    _chain[i].hash,
                  ].join('\n'),
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4),
                ),
              ),
            ),
          const SizedBox(height: 8),
          ExpansionTile(
            title: const Text('Advanced'),
            childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            children: [
              TextField(
                controller: _confidence,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Confidence, from 0 to 1'),
              ),
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton(
                  onPressed: () => setState(() => _status = _runVerify()),
                  child: const Text('Check links'),
                ),
              ),
              const SizedBox(height: 8),
              const Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'A timeslate is a receipt stored on this device. Author: Aziel Eliab.',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
