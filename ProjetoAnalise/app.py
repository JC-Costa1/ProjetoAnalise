import customtkinter as ctk
import sqlite3
from tkinter import messagebox
import os

# Importações necessárias para o PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuração do tema da interface
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppQualidade(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestão da Qualidade - Cajuína São Geraldo")
        self.geometry("1100x800")

        self.label_titulo = ctk.CTkLabel(self, text="LAUDO DE ANÁLISE E AVALIAÇÃO DE GARRAFAS SOPRADAS", font=("Arial", 18, "bold"))
        self.label_titulo.pack(pady=10)

        self.scroll_container = ctk.CTkScrollableFrame(self, width=1050, height=700)
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.criar_secao_informacoes_gerais()
        self.criar_secao_medicoes()
        
        frame_botoes = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        frame_botoes.pack(pady=20)

        self.btn_salvar = ctk.CTkButton(
            frame_botoes, text="1. Salvar no Banco de Dados", command=self.salvar_dados, 
            fg_color="#1f538d", font=("Arial", 13, "bold"), width=220, height=40
        )
        self.btn_salvar.grid(row=0, column=0, padx=10)

        self.btn_pdf = ctk.CTkButton(
            frame_botoes, text="2. Gerar PDF Padronizado (REG-SOP-0001)", command=self.gerar_pdf_formulario, 
            fg_color="green", font=("Arial", 13, "bold"), width=280, height=40
        )
        self.btn_pdf.grid(row=0, column=1, padx=10)

        self.ultimo_id_salvo = None

    def criar_secao_informacoes_gerais(self):
        frame_info = ctk.CTkFrame(self.scroll_container)
        frame_info.pack(fill="x", padx=10, pady=10)

        lbl_sec = ctk.CTkLabel(frame_info, text="INFORMAÇÕES GERAIS", font=("Arial", 14, "bold"))
        lbl_sec.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(frame_info, text="Data do Ensaio (AAAA-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_data_ensaio = ctk.CTkEntry(frame_info, placeholder_text="2026-09-18")
        self.ent_data_ensaio.grid(row=1, column=1, padx=5, pady=5)
        self.ent_data_ensaio.insert(0, "2026-09-18")

        ctk.CTkLabel(frame_info, text="Cor da Pré-forma:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.ent_cor_preforma = ctk.CTkEntry(frame_info, placeholder_text="VERDE")
        self.ent_cor_preforma.grid(row=1, column=3, padx=5, pady=5)
        self.ent_cor_preforma.insert(0, "VERDE")

        ctk.CTkLabel(frame_info, text="Lote de Fabricação:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ent_lote = ctk.CTkEntry(frame_info)
        self.ent_lote.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_info, text="Tipo de Resina:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.ent_resina = ctk.CTkEntry(frame_info, placeholder_text="RAMAPET")
        self.ent_resina.grid(row=2, column=3, padx=5, pady=5)
        self.ent_resina.insert(0, "RAMAPET")

        ctk.CTkLabel(frame_info, text="TAG Sopradora:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.combo_sopradora = ctk.CTkComboBox(frame_info, values=["SPR-01", "SPR-02", "SPR-03"], command=self.atualizar_quantidade_moldes)
        self.combo_sopradora.grid(row=3, column=1, padx=5, pady=5)
        self.combo_sopradora.set("SPR-01")

        ctk.CTkLabel(frame_info, text="Gramatura (g):").grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.ent_gramatura = ctk.CTkEntry(frame_info)
        self.ent_gramatura.grid(row=3, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame_info, text="Executor:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.ent_executor = ctk.CTkEntry(frame_info)
        self.ent_executor.grid(row=4, column=1, padx=5, pady=5)

    def criar_secao_medicoes(self):
        self.frame_tabela = ctk.CTkFrame(self.scroll_container)
        self.frame_tabela.pack(fill="x", padx=10, pady=10)

        lbl_sec = ctk.CTkLabel(self.frame_tabela, text="RESULTADOS DAS MEDIÇÕES", font=("Arial", 14, "bold"))
        lbl_sec.grid(row=0, column=0, columnspan=6, padx=10, pady=5, sticky="w")

        headers = ["Molde", "Finish (C/NC)", "Resist. Química (C/NC)", "Resist. Física (C/NC)", "Pressão (BAR)", "Status Pressão"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.frame_tabela, text=h, font=("Arial", 11, "bold")).grid(row=1, column=col, padx=10, pady=5)

        self.moldes_inputs = []
        self.atualizar_quantidade_moldes("SPR-01")

    def atualizar_quantidade_moldes(self, sopradora_selecionada):
        for widget in self.frame_tabela.winfo_children():
            if int(widget.grid_info()["row"]) > 1:
                widget.destroy()

        self.moldes_inputs.clear()

        qtd_moldes = 10
        if sopradora_selecionada == "SPR-02": qtd_moldes = 6
        elif sopradora_selecionada == "SPR-03": qtd_moldes = 8

        for i in range(1, qtd_moldes + 1):
            num_molde_str = f"{i:02d}"
            row_idx = i + 1

            ctk.CTkLabel(self.frame_tabela, text=num_molde_str).grid(row=row_idx, column=0, padx=5, pady=2)
            combo_finish = ctk.CTkComboBox(self.frame_tabela, values=["C", "NC"], width=70)
            combo_finish.grid(row=row_idx, column=1, padx=5, pady=2)
            combo_quimica = ctk.CTkComboBox(self.frame_tabela, values=["C", "NC"], width=70)
            combo_quimica.grid(row=row_idx, column=2, padx=5, pady=2)
            combo_fisica = ctk.CTkComboBox(self.frame_tabela, values=["C", "NC"], width=70)
            combo_fisica.grid(row=row_idx, column=3, padx=5, pady=2)
            
            ent_pressao = ctk.CTkEntry(self.frame_tabela, width=80, placeholder_text="0.0")
            ent_pressao.grid(row=row_idx, column=4, padx=5, pady=2)
            
            lbl_status_pressao = ctk.CTkLabel(self.frame_tabela, text="-", font=("Arial", 11, "bold"))
            lbl_status_pressao.grid(row=row_idx, column=5, padx=5, pady=2)

            # Evento para mudar C/NC em tempo real ao escrever
            ent_pressao.bind("<KeyRelease>", lambda event, entry=ent_pressao, lbl=lbl_status_pressao: self.validar_pressao(entry, lbl))
            
            # NOVO EVENTO: Saltar para o próximo input ao carregar no "Enter"
            ent_pressao.bind("<Return>", lambda event, idx=i-1: self.focar_proxima_pressao(event, idx))

            self.moldes_inputs.append({
                "molde": num_molde_str, "finish": combo_finish, "quimica": combo_quimica,
                "fisica": combo_fisica, "pressao": ent_pressao, "pressao_status": lbl_status_pressao
            })

    # NOVA FUNÇÃO: Move o cursor para a próxima linha
    def focar_proxima_pressao(self, event, index_atual):
        proximo_index = index_atual + 1
        # Se ainda houver linhas de pressão em baixo
        if proximo_index < len(self.moldes_inputs):
            self.moldes_inputs[proximo_index]["pressao"].focus_set()
        else:
            # Se for a última linha, foca no botão de salvar
            self.btn_salvar.focus_set()

    def validar_pressao(self, entry, label):
        try:
            valor = float(entry.get().replace(",", "."))
            if valor >= 10.0:
                label.configure(text="C", text_color="green")
            else:
                label.configure(text="NC", text_color="red")
        except ValueError:
            label.configure(text="-", text_color="gray")

    def salvar_dados(self):
        try:
            conn = sqlite3.connect('banco_qualidade.db')
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO inspecao_cabecalho (data_ensaio, cor_preforma, lote_fabricacao, tipo_resina, tag_sopradora, gramatura, executor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.ent_data_ensaio.get(), self.ent_cor_preforma.get(), self.ent_lote.get(),
                self.ent_resina.get(), self.combo_sopradora.get(), self.ent_gramatura.get(), self.ent_executor.get()
            ))

            self.ultimo_id_salvo = cursor.lastrowid

            for item in self.moldes_inputs:
                cursor.execute('''
                INSERT INTO medicao_molde (id_inspecao, numero_molde, finish_status, resistencia_quimica_status, resistencia_fisica_status, pressao_estouro_bar, pressao_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.ultimo_id_salvo, int(item["molde"]), item["finish"].get(), item["quimica"].get(),
                    item["fisica"].get(), item["pressao"].get(), item["pressao_status"].cget("text")
                ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", f"Registro #{self.ultimo_id_salvo} salvo com sucesso no banco de dados!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar no banco: {e}")

    def gerar_pdf_formulario(self):
        if not self.ultimo_id_salvo:
            self.salvar_dados()
            if not self.ultimo_id_salvo: return

        nome_pdf = f"REG-SOP-0001_ID_{self.ultimo_id_salvo}.pdf"
        
        doc = SimpleDocTemplate(
            nome_pdf, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm
        )

        elements = []
        styles = getSampleStyleSheet()

        estilo_tit_cab = ParagraphStyle('TitCab', fontName='Helvetica-Bold', fontSize=10, leading=11, alignment=1)
        estilo_info_cab = ParagraphStyle('InfCab', fontName='Helvetica', fontSize=8, leading=10)
        estilo_normal = ParagraphStyle('Norm', fontName='Helvetica', fontSize=9, leading=12)
        estilo_bold = ParagraphStyle('NormB', fontName='Helvetica-Bold', fontSize=9, leading=12)
        estilo_nota = ParagraphStyle('Nota', fontName='Helvetica', fontSize=8, leading=10, alignment=4)
        estilo_cab_tab = ParagraphStyle('CabTab', fontName='Helvetica-Bold', fontSize=7, leading=9, alignment=1)
        estilo_cel = ParagraphStyle('Cel', fontName='Helvetica', fontSize=8, leading=10, alignment=1)

        def criar_cabecalho(pagina):
            caminho_logo = "logo_sao_geraldo.jpg" 
            if os.path.exists(caminho_logo):
                logo = Image(caminho_logo, width=3.0*cm, height=1.5*cm)
            else:
                logo = Paragraph("<b>SÃO GERALDO</b>", estilo_tit_cab)

            estilo_classificacao = ParagraphStyle('Classif', fontName='Helvetica-Bold', fontSize=7, alignment=0)

            # 1. CRIAMOS A TABELA INTERNA (Apenas para o bloco da direita)
            dados_lateral = [
                [Paragraph("<b>N°:</b> REG-SOP-0001", estilo_info_cab)],
                [Paragraph("<b>REVISÃO:</b> 2", estilo_info_cab)],
                [Paragraph(f"<b>PÁGINAS:</b> Página {pagina} de 2", estilo_info_cab)]
            ]
            
            tabela_lateral = Table(dados_lateral, colWidths=[4.5*cm])
            tabela_lateral.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black), # Desenha as linhas horizontais de divisão
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 5), # Dá um pequeno espaço para o texto não colar na linha
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))

            # 2. TABELA PRINCIPAL
            return Table([
                [
                    logo,
                    Paragraph("<b>LAUDO DE ANÁLISE E AVALIAÇÃO DO DESEMPENHO DAS GARRAFAS SOPRADAS</b>", estilo_tit_cab),
                    tabela_lateral # Inserimos a tabela interna aqui, em vez do texto solto
                ],
                [
                    "", 
                    Paragraph("<b>CLASSIFICAÇÃO:</b> Registro", estilo_classificacao),
                    ""  
                ]
            ], colWidths=[3.5*cm, 9.0*cm, 4.5*cm], style=TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('SPAN', (0,0), (0,1)),
                ('SPAN', (2,0), (2,1)),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (0,1), 'CENTER'),
                
                # Zera as margens da célula do canto direito para as linhas tocarem na borda principal
                ('LEFTPADDING', (2,0), (2,1), 0),
                ('RIGHTPADDING', (2,0), (2,1), 0),
                ('TOPPADDING', (2,0), (2,1), 0),
                ('BOTTOMPADDING', (2,0), (2,1), 0),
            ]))
        
        def criar_rodape_aprovacoes():
            # Estilo dedicado para centralizar o texto das aprovações
            estilo_aprovacao = ParagraphStyle(
                'ApvCent', 
                fontName='Helvetica', 
                fontSize=8, 
                leading=10, 
                alignment=1 # 1 = Centralizado
            )

            dados_aprovacao = [
                [
                    Paragraph("ELABORADO POR:<br/><br/><b>Weskley Rodrigues Monteiro</b><br/>Assistente de Processos<br/>02/07/2026", estilo_aprovacao),
                    Paragraph("REVISADO POR:<br/><br/><b>Rodrigues Pereira</b><br/>Assistente de Processos<br/>17/08/2026", estilo_aprovacao),
                    Paragraph("APROVADO POR:<br/><br/><b>Wanderson Rabelo</b><br/>Coordenador de Qualidade<br/>17/08/2026", estilo_aprovacao),
                ]
            ]

            tabela_interna = Table(dados_aprovacao, colWidths=[5.66*cm, 5.66*cm, 5.68*cm])
            tabela_interna.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black), # Desenha a linha divisória entre as colunas
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'), # Centraliza o conteúdo horizontalmente
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6)
            ]))

            return Table([
                [Paragraph("<b>APROVAÇÕES</b>", estilo_tit_cab)],
                [tabela_interna]
            ], colWidths=[17.0*cm], style=TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,1), (0,1), 0),
                ('RIGHTPADDING', (0,1), (0,1), 0),
                ('TOPPADDING', (0,1), (0,1), 0),
                ('BOTTOMPADDING', (0,1), (0,1), 0),
            ]))

        # PÁGINA 1
        elements.append(criar_cabecalho(1))
        elements.append(Spacer(1, 10))

        # ALTERA PARA O TÍTULO CORRETO:
        # Estilo centralizado para o novo título dentro da tabela
        estilo_info_titulo = ParagraphStyle('InfoTit', fontName='Helvetica-Bold', fontSize=10, alignment=1)

        dados_info = [
            # Nova linha 0: O título mesclado
            [Paragraph("INFORMAÇÕES GERAIS", estilo_info_titulo), ""],
            
            # Restantes linhas de dados
            [Paragraph(f"<b>Cor da pré-forma:</b> {self.ent_cor_preforma.get()}", estilo_normal), Paragraph(f"<b>Data do ensaio:</b> {self.ent_data_ensaio.get()}", estilo_normal)],
            [Paragraph(f"<b>Lote de fabricação:</b> {self.ent_lote.get()}", estilo_normal), Paragraph(f"<b>TAG Sopradora:</b> {self.combo_sopradora.get()}", estilo_normal)],
            [Paragraph(f"<b>Tipo de resina:</b> {self.ent_resina.get()}", estilo_normal), Paragraph(f"<b>Gramatura:</b> {self.ent_gramatura.get()} g", estilo_normal)],
            [Paragraph("<b>SKU do produto:</b> 2L( ) 1L( ) 200mL( ) Outro: ____", estilo_normal), ""],
            [Paragraph("<b>Fornecedor:</b> BRASALPLA", estilo_normal), Paragraph(f"<b>Executor:</b> {self.ent_executor.get()}", estilo_normal)]
        ]
        
        tabela_info = Table(dados_info, colWidths=[8.5*cm, 8.5*cm])
        tabela_info.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black), 
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Regras exclusivas para a primeira linha (o título)
            ('SPAN', (0,0), (1,0)), # Mescla as duas colunas
            ('BACKGROUND', (0,0), (1,0), colors.lightgrey), # Fundo cinza
            ('ALIGN', (0,0), (1,0), 'CENTER'), # Centraliza o texto
            ('TOPPADDING', (0,0), (1,0), 5),
            ('BOTTOMPADDING', (0,0), (1,0), 5)
        ]))
        
        elements.append(tabela_info)
        elements.append(Spacer(1, 10))

        texto_nota = (
            "<b>NOTA 01:</b> As medições devem ser registradas seguindo obrigatoriamente a quantidade de moldes definida para cada sopradora. O número de medições realizadas varia conforme a sopradora utilizada, conforme descrito abaixo:<br/><br/>"
            "Sopradora SPR-01: realizar medições de 10 moldes.<br/>"
            "Sopradora SPR-02: realizar medições de 06 moldes.<br/>"
            "Sopradora SPR-03: realizar medições de 08 moldes.<br/><br/>"
            "<b>C = CONFORME / NC = NÃO CONFORME</b>"
        )
        
        elements.append(Paragraph(texto_nota, estilo_nota))
        elements.append(Spacer(1, 15))
# 1. LINHA 0: Títulos principais
        tit_moldes = Paragraph("<b>Moldes:</b>", estilo_cab_tab)
        tit_finish = Paragraph("<b>FINISH</b>", estilo_cab_tab)
        tit_quimica = Paragraph("<b>RESISTÊNCIA QUÍMICA</b>", estilo_cab_tab)
        tit_fisica = Paragraph("<b>RESISTÊNCIA FÍSICA</b>", estilo_cab_tab)
        tit_pressao = Paragraph("<b>PRESSÃO INTERNA</b>", estilo_cab_tab)

        # 2. LINHA 1: Horários
        sub_horario = Paragraph("Horário do teste:<b> _____</b>", estilo_cab_tab)
        
        # 3. LINHA 2: Critérios
        sub_moldes_crit = Paragraph("<b>Critério de<br/>aceitação:</b>", estilo_cab_tab)
        sub_finish_crit = Paragraph("PASSA = 28,16mm<br/>NÃO PASSA = 27,53mm", estilo_cab_tab)
        sub_quimica_fisica_crit = Paragraph("NÃO ESTOURAR OU RACHAR<br/>O FUNDO DA GARRAFA", estilo_cab_tab)
        sub_pressao_crit = Paragraph("Pressão de estouro<br/>NÃO ESTOURAR COM<br/>PRESSÃO ABAIXO DE 10 BAR", estilo_cab_tab)

        # 4. CONSTRUÇÃO DAS TRÊS LINHAS NO TOPO DA TABELA
        tabela_medicoes_dados = [
            # Linha 0: Topo
            [tit_moldes, tit_finish, tit_quimica, tit_fisica, tit_pressao], 
            
            # Linha 1: Horários. A célula "" será "engolida" pelo Moldes (que vem de cima).
            ["", sub_horario, sub_horario, sub_horario, sub_horario],
            
            # Linha 2: Critérios. A célula "" será "engolida" pelo texto da resistência (que vem do lado).
            [sub_moldes_crit, sub_finish_crit, sub_quimica_fisica_crit, "", sub_pressao_crit] 
        ]

        # Loop dos inputs (mantém-se igual)
        for item in self.moldes_inputs:
            fin = "(X) C ( ) NC" if item["finish"].get() == "C" else "( ) C (X) NC"
            qui = "(X) C ( ) NC" if item["quimica"].get() == "C" else "( ) C (X) NC"
            fis = "(X) C ( ) NC" if item["fisica"].get() == "C" else "( ) C (X) NC"
            pre = "(X) C ( ) NC" if item["pressao_status"].cget("text") == "C" else "( ) C (X) NC"
            bar = f"{item['pressao'].get()} bar"
            tabela_medicoes_dados.append([Paragraph(item["molde"], estilo_cel), Paragraph(fin, estilo_cel), Paragraph(qui, estilo_cel), Paragraph(fis, estilo_cel), Paragraph(f"{pre}<br/>{bar}", estilo_cel)])

        tabela_medicoes = Table(tabela_medicoes_dados, colWidths=[2.0*cm, 3.4*cm, 3.5*cm, 3.8*cm, 4.3*cm])
        
        # 5. APLICAR O ESTILO
        tabela_medicoes.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black), 
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black), 
            
            # Mescla a coluna 0 ("Moldes:") para ocupar a Linha 0 e a Linha 1
            ('SPAN', (0,0), (0,1)), 
            
            # Mescla a Química e Física apenas na Linha 2 (onde estão os critérios)
            ('SPAN', (2,2), (3,2)), 
            
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            
            # =================================================================
            # A MAGIA DA ALTURA DAS LINHAS ACONTECE AQUI:
            
            # 1. Aumenta o espaço (altura) apenas das 3 linhas do cabeçalho (Linhas 0, 1 e 2)
            ('TOPPADDING', (0,0), (-1,2), 8),
            ('BOTTOMPADDING', (0,0), (-1,2), 8),
            
            # 2. Diminui o espaço (achatando) das linhas enumeradas (Linha 3 até ao fim)
            ('TOPPADDING', (0,3), (-1,-1), 1),
            ('BOTTOMPADDING', (0,3), (-1,-1), 1)
            # =================================================================
        ]))
        
        elements.append(tabela_medicoes)
        elements.append(Spacer(1, 25))
        elements.append(criar_rodape_aprovacoes())

        # PÁGINA 2
        elements.append(PageBreak())
        elements.append(criar_cabecalho(2))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>OBSERVAÇÕES:</b>", estilo_bold))
        tabela_obs = Table([["\n\n\n\n\n"]], colWidths=[17.0*cm])
        tabela_obs.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(tabela_obs)
        elements.append(Spacer(1, 10))

        nota_02 = ("<b>NOTA 02:</b> Os ensaios de regularidade do finish, resistência química do fundo, resistência física do fundo e resistência à pressão interna devem ser realizados conforme procedimento internos do setor de Sopro. Os resultados apresentados deve ser conferidos e validados pela Gestão da Qualidade, mediante assinatura neste documento.")
        nota_03 = ("<b>NOTA 03:</b> Em caso de não conformidade, realizar o reteste imediato com três amostras adicionais do mesmo molde. Registrar os resultados detalhadamente no campo de observações. Caso a falha persista, proceda com os ajustes no processo e a abertura formal de 'Ocorrência' via sistema 'Qualiex'.")
        elements.append(Paragraph(nota_02, estilo_nota))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(nota_03, estilo_nota))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>Assinatura da Gestão da Qualidade:</b> ____________________________________    <b>Data:</b> ___/___/___", estilo_normal))
        elements.append(Spacer(1, 15))

        dados_revisao = [
            [Paragraph("<b>REVISÃO</b>", estilo_cab_tab), Paragraph("<b>DATA</b>", estilo_cab_tab), Paragraph("<b>RESPONSÁVEL</b>", estilo_cab_tab), Paragraph("<b>HISTÓRICO ALTERAÇÃO</b>", estilo_cab_tab)],
            [Paragraph("0", estilo_cel), Paragraph("05.12.2024", estilo_cel), Paragraph("Leandro Gonçalves", estilo_cel), Paragraph("Emissão inicial", estilo_cel)],
            [Paragraph("1", estilo_cel), Paragraph("06.03.2026", estilo_cel), Paragraph("Weskley Rodrigues", estilo_cel), Paragraph("Revisão integral do escopo para unificação de processos. Os documentos REG SOP 0002, REG SOP 0003 e REG SOP 0004 foram integrados a esta versão, sendo descontinuados (obsoletados) como registros individuais a partir da data de aprovação.", estilo_cel)],
            [Paragraph("2", estilo_cel), Paragraph("02.07.2026", estilo_cel), Paragraph("Weskley Rodrigues", estilo_cel), Paragraph("Alteração na Nota 02 da validação do documento e do campo de assinatura da 'Produção' para a 'Qualidade'", estilo_cel)]
        ]
        tabela_revisao = Table(dados_revisao, colWidths=[2.0*cm, 2.5*cm, 3.5*cm, 9.0*cm])
        tabela_revisao.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)]))
        elements.append(tabela_revisao)
        elements.append(Spacer(1, 15))
        
        elements.append(criar_rodape_aprovacoes())

        doc.build(elements)
        messagebox.showinfo("PDF Gerado", f"O laudo padronizado foi gerado com sucesso:\n{nome_pdf}")

if __name__ == "__main__":
    app = AppQualidade()
    app.mainloop()